"""Validate the three trusted local FD001 inputs. Run from the repository root."""
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
import platform
import re
from pathlib import Path

import numpy as np


DATA = Path("data/FD001")
OUT = Path(__file__).resolve().parents[1] / "local_only" / "reproduced"
FILES = {"train": "train_FD001.txt", "test": "test_FD001.txt", "rul": "RUL_FD001.txt"}
HASHES = {
    "train": "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8",
    "test": "3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851",
    "rul": "a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca",
}
COLUMNS = ["unit_id", "cycle", *[f"setting_{i}" for i in range(1, 4)],
           *[f"sensor_{i}" for i in range(1, 22)]]
BASIS = "MathWorks FD001 localLoadData: RUL record i belongs to test unit at ascending unique-ID rank i."
REFERENCE = "https://it.mathworks.com/help/predmaint/ug/remaining-useful-life-estimation-using-convolutional-neural-network.html"


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def check(checks, name, expected, actual):
    ok = actual == expected
    checks.append(dict(name=name, expected=expected, actual=actual,
                       status="PASS" if ok else "FAIL", original_error=None if ok else "Mismatch"))
    if not ok:
        raise ValueError(f"{name}: expected {expected}, actual {actual}")


def read_lines(path):
    with path.open("rb") as f:
        return [line.decode("ascii") for line in f]


def locate(split, lines, column, *, unit=None, cycle=None, record=None):
    columns = ["final_RUL"] if split == "rul" else COLUMNS
    pos = columns.index(column)
    index = 0
    for physical, line in enumerate(lines, 1):
        tokens = line.split()
        if not tokens:
            continue
        index += 1
        if split == "rul":
            matches = index == record
        else:
            matches = (int(tokens[0]), int(tokens[1])) == (unit, cycle)
        if matches:
            token = tokens[pos]
            return dict(dataset_id="FD001", split=split, source_filename=FILES[split],
                        source_sha256=HASHES[split], source_record_index=index,
                        source_physical_line=physical, unit_id=unit, cycle=cycle,
                        column_name=column, column_position=pos+1, original_value=token,
                        parsed_value=float(token))
    raise LookupError("No matching source record")


def inspect(split, checks):
    path = DATA / FILES[split]
    cols = ["final_RUL"] if split == "rul" else COLUMNS
    before = path.read_bytes()
    check(checks, split+" pinned local SHA256", HASHES[split], hashlib.sha256(before).hexdigest())
    lines = read_lines(path)
    tokens = [line.split() for line in lines if line.strip()]
    widths = Counter(map(len, tokens))
    check(checks, split+" observed widths", [len(cols)], sorted(widths))
    physical = [i for i, line in enumerate(lines, 1) if line.strip()]
    # Independent parser reopens the file with its own whitespace tokenizer.
    arr = np.loadtxt(path, comments=None, ndmin=2, encoding="ascii")
    check(checks, split+" independent shape", [len(tokens), len(cols)], list(arr.shape))
    physical_ref = len(before.splitlines())
    check(checks, split+" physical lines", physical_ref, len(lines))
    decimal_rows = [[Decimal(v) for v in row] for row in tokens]
    bad = sum(not v.is_finite() for row in decimal_rows for v in row)
    check(checks, split+" independent nonfinite count", bad, int((~np.isfinite(arr)).sum()))
    check(checks, split+" invalid or nonfinite entries", 0, bad)
    check(checks, split+" empty/missing fields or NaN", 0, int(np.isnan(arr).sum()))
    check(checks, split+" all parsed values agree", True,
          bool(np.array_equal(arr, np.asarray(decimal_rows, dtype=float))))
    summaries = []
    for i, name in enumerate(cols):
        vals, counts = np.unique(arr[:, i], return_counts=True)
        dominant = int(counts.max())
        integer_field = name in ("unit_id", "cycle", "final_RUL")
        if integer_field:
            check(checks, split+" "+name+" noninteger values", 0,
                  sum(row[i] != row[i].to_integral_value() for row in decimal_rows))
        summaries.append(dict(position=i+1, name=name, logical_dtype="integer" if integer_field else "real",
                              numeric_parser_dtype=str(arr.dtype), distinct=len(vals),
                              min=float(vals.min()), max=float(vals.max()), dominant_count=dominant,
                              dominant_fraction=dominant/len(arr), constant=len(vals)==1,
                              near_constant=len(vals)>1 and dominant/len(arr)>=0.99))
    units = []
    repeats = int(len(arr) - len(np.unique(arr, axis=0)))
    check(checks, split+" duplicate-record counts", len(tokens)-len(set(map(tuple, decimal_rows))), repeats)
    if split != "rul":
        keys = [(int(row[0]), int(row[1])) for row in tokens]
        check(checks, split+" ordered cycle keys", True, keys == [tuple(row) for row in arr[:, :2]])
        check(checks, split+" duplicate keys", 0, len(keys)-len(set(keys)))
        ids = sorted(set(u for u, _ in keys))
        check(checks, split+" independent IDs", ids, np.unique(arr[:, 0]).astype(int).tolist())
        for u in ids:
            cycles = arr[arr[:, 0]==u, 1].astype(int).tolist()
            gaps = max(cycles) - min(cycles) + 1 - len(set(cycles))
            units.append(dict(unit_id=u, cycle_count=len(cycles), first_observed_cycle=cycles[0],
                              last_observed_cycle=cycles[-1], strictly_increasing=all(
                                  b>a for a,b in zip(cycles, cycles[1:])),
                              duplicate_cycles=len(cycles)-len(set(cycles)), internal_missing_cycles=gaps))
        check(checks, split+" contiguous cycles starting at one in source order", True,
              all(u["first_observed_cycle"]==1 and u["strictly_increasing"] and
                  u["internal_missing_cycles"]==0 for u in units))
    else:
        check(checks, "RUL negative values", 0, int((arr < 0).sum()))
    samples = []
    for idx, col in [(0,0 if split=="rul" else 5),
                     (len(arr)//2,0 if split=="rul" else 15), (len(arr)-1,len(cols)-1)]:
        kwargs = dict(record=idx+1) if split=="rul" else dict(unit=int(arr[idx,0]),cycle=int(arr[idx,1]))
        found = locate(split, lines, cols[col], **kwargs)
        fields = re.findall(rb"\S+", before.splitlines()[found["source_physical_line"]-1])
        match = (found["source_record_index"]==idx+1 and found["source_physical_line"]==physical[idx]
                 and found["column_position"]==col+1 and found["parsed_value"]==arr[idx,col]
                 and found["original_value"]==fields[col].decode("ascii"))
        check(checks, f"{split} raw locator record {idx+1} column {col+1}", True, bool(match))
        samples.append(found)
    with path.open("rb") as f:
        after = hashlib.file_digest(f, "sha256").hexdigest()
    check(checks, split+" SHA256 after analysis", HASHES[split], after)
    inv = dict(filename=FILES[split], relative_path=path.as_posix(), size_bytes=len(before), sha256=after,
               encoding="ASCII (all bytes decoded strictly)", physical_lines=len(lines),
               valid_records=len(arr), logical_columns=len(cols), blank_lines=len(lines)-len(arr),
               trailing_whitespace_lines=sum(s.rstrip("\r\n").endswith((" ", "\t")) for s in lines),
               delimiter="Runs of ASCII whitespace; blank lines excluded from record numbering.",
               read_status="READ_OK", errors=[], warnings=[])
    quality = dict(missing_values=0, invalid_numeric=0, nan=0, infinity=0, duplicate_records=repeats,
                   constant_columns=[s["name"] for s in summaries if s["constant"]],
                   near_constant_columns=[s["name"] for s in summaries if s["near_constant"]])
    return inv, summaries, units, quality, samples, arr, physical


def validate(out, checks):
    inventories, schemas, indexes, quality, locators = {}, {}, {}, {}, []
    for split in FILES:
        inv, schema, units, qc, sample, arr, physical = inspect(split, checks)
        inventories[split], schemas[split], quality[split] = inv, schema, qc
        locators.extend(sample)
        if split != "rul":
            indexes[split] = units
        else:
            rul = arr[:, 0].astype(int).tolist()
            rul_lines = physical
        print(f"{split}: physical={inv['physical_lines']} valid={inv['valid_records']} cols={inv['logical_columns']} sha256={inv['sha256']}")
    check(checks, "train/test schema", [(c["name"], c["logical_dtype"]) for c in schemas["train"]],
          [(c["name"], c["logical_dtype"]) for c in schemas["test"]])
    test_units = indexes["test"]
    check(checks, "test ID ranks are contiguous and 1-based", list(range(1,len(test_units)+1)),
          [u["unit_id"] for u in test_units])
    check(checks, "one RUL for each independently validated test-unit rank", len(test_units), len(rul))
    mapping = [dict(unit_id=u["unit_id"], last_observed_cycle=u["last_observed_cycle"], final_RUL=v,
                    rul_source_record_index=i, rul_source_physical_line=line, mapping_basis="MW_FD001_SORTED_ID")
               for i,(u,v,line) in enumerate(zip(test_units,rul,rul_lines,strict=True),1)]
    # Re-read the original label lines for every assigned row, independently of the NumPy parse.
    source = read_lines(DATA/FILES["rul"])
    for row in mapping:
        if row["final_RUL"] != int(source[row["rul_source_physical_line"]-1]):
            raise ValueError("RUL source lookup mismatch")
    check(checks, "RUL labels traced to source by verified rank", len(rul), len(mapping))
    for split, name in FILES.items():
        check(checks, split+" final input stability", HASHES[split], hashlib.sha256((DATA/name).read_bytes()).hexdigest())
    save(out/"file_inventory.json",inventories)
    save(out/"local_only"/"resolved_paths.json",{s:str((DATA/f).resolve(strict=True)) for s,f in FILES.items()})
    save(out/"raw_schema.json",schemas)
    save(out/"unit_cycle_index.json",indexes)
    save(out/"rul_mapping.json",dict(status="VERIFIED_BY_REFERENCE_CONVENTION", unit_count=len(mapping),
         basis_id="MW_FD001_SORTED_ID",basis=BASIS,reference=REFERENCE,
         private_mapping="local_only/rul_by_unit.json", independent_unit_key_in_rul=False))
    save(out/"local_only"/"rul_by_unit.json",mapping)
    save(out/"local_only"/"locator_samples.json",locators)
    save(out/"quality.json",quality)
    print(f"{len(checks)} checks passed; test unit mappings={len(mapping)}; locator samples={len(locators)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    parser.add_argument("--locate",choices=FILES)
    parser.add_argument("--unit",type=int)
    parser.add_argument("--cycle",type=int)
    parser.add_argument("--column")
    parser.add_argument("--record",type=int)
    args = parser.parse_args()
    if args.locate:
        split = args.locate
        path = DATA/FILES[split]
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != HASHES[split]:
            raise ValueError("Source identity mismatch")
        if split == "rul":
            if args.record is None or args.unit is not None or args.cycle is not None:
                parser.error("RUL lookup requires --record")
        elif args.unit is None or args.cycle is None or args.column is None or args.record is not None:
            parser.error("Telemetry lookup requires --unit, --cycle and --column")
        print(json.dumps(locate(split,content.decode("ascii").splitlines(),args.column or "final_RUL",
                                unit=args.unit,cycle=args.cycle,record=args.record)))
        return
    checks = []
    print(f"Python {platform.python_version()} / NumPy {np.__version__}")
    try:
        validate(args.output, checks)
    except Exception as exc:
        checks.append(dict(name="validation stopped",expected="completed",actual="stopped",
                           status="FAIL",original_error=f"{type(exc).__name__}: {exc}"))
        raise
    finally:
        save(args.output/"checks.json",checks)


if __name__ == "__main__":
    main()
