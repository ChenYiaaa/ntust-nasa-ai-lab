"""Read-only FD001 query functions and JSON CLI. Uses Python's standard library."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
METADATA = json.loads((HERE / "fd001_data_contract.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((HERE / "fd001_column_schema.json").read_text(encoding="utf-8"))
ERRORS = json.loads((HERE / "fd001_error_contract.json").read_text(encoding="utf-8"))["errors"]
SENSORS = {c["sensor_id"]: c for c in SCHEMA["columns"] if "sensor_id" in c}
RUL_RULE = METADATA["rul"]
RAW_VERIFIED = "VERIFIED_LOCAL_SOURCE"


class ContractError(Exception):
    def __init__(self, code, **context):
        definition = ERRORS[code]
        self.payload = dict(error_code=code, message=definition["message"],
                            input_context=context, recoverability=definition["recoverability"])
        super().__init__(definition["message"])


def verified_records(directory, source):
    filename = METADATA["source_files"][source]
    try:
        data = (directory / filename).read_bytes()
        if hashlib.sha256(data).hexdigest() != METADATA["source_sha256"][source]:
            raise ValueError("SHA-256 mismatch")
        lines = data.decode("ascii").splitlines()
    except (OSError, ValueError) as exc:
        raise ContractError("SOURCE_NOT_VERIFIED", source_filename=filename) from exc
    return [(number, line.split()) for number, line in enumerate(lines, 1) if line.strip()]


def telemetry_index(records, split):
    grouped = defaultdict(dict)
    try:
        for record_index, (physical_line, fields) in enumerate(records, 1):
            unit, cycle = map(int, fields[:2])
            values = tuple(map(float, fields[2:]))
            if len(fields) != len(SCHEMA["columns"]) or not all(map(math.isfinite, values)):
                raise ValueError("Invalid telemetry record")
            trajectory = grouped[unit]
            if cycle != len(trajectory) + 1 or unit < 1:
                raise ValueError("Unit or Cycle index is invalid")
            trajectory[cycle] = (record_index, physical_line, values)
        if len(records) != METADATA["row_counts"][split] or len(grouped) != METADATA["unit_counts"][split]:
            raise ValueError("Unexpected verified source shape")
    except ValueError as exc:
        raise ContractError("SOURCE_NOT_VERIFIED", source_filename=METADATA["source_files"][split]) from exc
    return dict(grouped)


def map_rul(unit_ids, records):
    ids = sorted(unit_ids)
    try:
        if ids != list(range(1, len(ids) + 1)) or len(ids) != len(records) or not ids:
            raise ValueError("RUL cardinality or unit rank is invalid")
        mapping = {}
        for index, (unit, (_, fields)) in enumerate(zip(ids, records, strict=True), 1):
            (token,) = fields
            value = int(token)
            if value < 0:
                raise ValueError("Negative RUL")
            mapping[unit] = (index, value)
        return mapping
    except ValueError as exc:
        raise ContractError("RUL_MAPPING_INVALID", split="test",
                            unit_count=len(ids), rul_records=len(records)) from exc


class FD001:
    """Verified read-only in-memory snapshot. Construct again to recheck files on disk."""

    def __init__(self, source_dir=Path("data/FD001")):
        directory = Path(source_dir)
        self._indexes = {s: telemetry_index(verified_records(directory, s), s)
                         for s in METADATA["available_splits"]}
        self._rul = map_rul(self._indexes["test"], verified_records(directory, "rul"))

    def _split(self, split):
        if split not in METADATA["available_splits"]:
            raise ContractError("INVALID_SPLIT", split=split)
        return self._indexes[split]

    def _unit(self, split, unit_id):
        index = self._split(split)
        if type(unit_id) is not int or unit_id not in index:
            raise ContractError("UNKNOWN_UNIT", split=split, unit_id=unit_id)
        return index[unit_id]

    def units(self, split):
        return dict(split=split, unit_ids=sorted(self._split(split)))

    def sensors(self):
        return dict(sensors=[dict(sensor) for sensor in SENSORS.values()])

    def unit(self, split, unit_id):
        trajectory = self._unit(split, unit_id)
        first, last = min(trajectory), max(trajectory)
        return dict(split=split, unit_id=unit_id, first_cycle=first, last_observed_cycle=last,
                    cycle_count=len(trajectory), source_filename=METADATA["source_files"][split],
                    source_sha256=METADATA["source_sha256"][split],
                    source_locator=dict(first=locator(trajectory[first]), last=locator(trajectory[last])))

    def sensor(self, split, unit_id, sensor_id, cycle_start, cycle_end):
        trajectory = self._unit(split, unit_id)
        if type(sensor_id) is not int or sensor_id not in SENSORS:
            raise ContractError("UNKNOWN_SENSOR", split=split, unit_id=unit_id, sensor_id=sensor_id)
        if (type(cycle_start) is not int or type(cycle_end) is not int
                or not min(trajectory) <= cycle_start <= cycle_end <= max(trajectory)
                or any(c not in trajectory for c in range(cycle_start, cycle_end + 1))):
            raise ContractError("CYCLE_OUT_OF_RANGE", split=split, unit_id=unit_id,
                                cycle_start=cycle_start, cycle_end=cycle_end,
                                first_cycle=min(trajectory), last_observed_cycle=max(trajectory))
        column = SENSORS[sensor_id]
        pos = column["column_position"]
        return [
            dict(dataset_id=METADATA["dataset_id"], split=split, unit_id=unit_id, sensor_id=sensor_id,
                 cycle=cycle, value=trajectory[cycle][2][pos - 3],
                 source_filename=METADATA["source_files"][split], source_sha256=METADATA["source_sha256"][split],
                 **locator(trajectory[cycle]), column_name=column["column_name"], column_position=pos,
                 verification_status=RAW_VERIFIED,
                 evidence=evidence(split, unit_id, sensor_id, cycle, [locator(trajectory[cycle], pos)],
                                   "Direct parse of verified ASCII source"))
            for cycle in range(cycle_start, cycle_end + 1)
        ]

    def trend(self, split, unit_id, sensor_id, cycle_start, cycle_end):
        rows = self.sensor(split, unit_id, sensor_id, cycle_start, cycle_end)
        xs = [row["cycle"] for row in rows]
        ys = [row["value"] for row in rows]
        slope = "NOT_APPLICABLE"
        reason = "fewer than two valid observations" if len(xs) < 2 else None
        if len(xs) >= 2:
            if min(xs) == max(xs):
                reason = "zero cycle variance"
            else:
                slope = statistics.linear_regression(xs, ys).slope if min(ys) != max(ys) else 0.0
        refs = [{**{key: row[key] for key in ("source_record_index","source_physical_line","column_position")},
                 "cycle":row["cycle"]} for row in rows]
        return dict(observation_count=len(ys), missing_count=0, minimum=min(ys), maximum=max(ys),
                    mean=statistics.mean(ys), standard_deviation=statistics.stdev(ys) if len(ys) >= 2 else "NOT_APPLICABLE",
                    trend_slope=slope, slope_reason=reason, slope_unit="UNKNOWN / Cycle",
                    evidence=evidence(split, unit_id, sensor_id, [cycle_start, cycle_end], refs,
                                      METADATA["evidence"]["trend_method"]))

    def rul(self, split, unit_id):
        if split != "test":
            raise ContractError("INVALID_SPLIT", split=split, operation="rul")
        trajectory = self._unit(split, unit_id)
        record, value = self._rul[unit_id]
        return dict(unit_id=unit_id, last_observed_cycle=max(trajectory), rul_at_last_observation=value,
                    rul_source_record_index=record, mapping_basis=RUL_RULE["mapping_basis"],
                    source_sha256=METADATA["source_sha256"]["rul"],
                    verification_status=RUL_RULE["mapping_status"])


def locator(row, position=None):
    ref = dict(source_record_index=row[0], source_physical_line=row[1])
    if position is not None:
        ref["column_position"] = position
    return ref


def evidence(split, unit_id, sensor_id, cycles, refs, method):
    return dict(source_filename=METADATA["source_files"][split], source_sha256=METADATA["source_sha256"][split],
                split=split, unit_id=unit_id, cycle_or_cycle_range=cycles, sensor_id=sensor_id,
                source_row_reference=refs, calculation_method=method, verification_status=RAW_VERIFIED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("data/FD001"))
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in METADATA["operations"]:
        op = sub.add_parser(name)
        for field in METADATA["operations"][name]["input"]:
            op.add_argument(field, type=str if field == "split" else int)
    args = vars(parser.parse_args())
    operation = args.pop("operation")
    directory = args.pop("source_dir")
    try:
        response = getattr(FD001(directory), operation)(**args)
    except ContractError as exc:
        print(json.dumps(exc.payload, ensure_ascii=False))
        return 2
    print(json.dumps(response, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
