"""Run from the repository root with the authorized local source available."""

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd


SOURCE = Path("data/synthetic_sensor.csv")
SHA256 = "cd536b46eb628909fdc986bbad956c24a2e50afb287968998374befc62204377"
COLUMNS = ["timestamp", "load_pct", "coolant_out_c", "oil_pressure_bar"]
CHANNELS = COLUMNS[1:]
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
NA = "NOT_APPLICABLE"
DATASET_ID = "synthetic_sensor"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def summarize_numeric(series, reference):
    values = series.dropna()
    result = {
        "count": int(values.count()),
        "mean": float(values.mean()),
        "standard_deviation": float(values.std(ddof=1)),
        "minimum": float(values.min()),
        "median": float(values.median()),
        "maximum": float(values.max()),
    }
    expected = (len(reference), statistics.mean(reference), statistics.stdev(reference),
                min(reference), statistics.median(reference), max(reference))
    for (metric, actual), target in zip(result.items(), expected, strict=True):
        require(math.isclose(actual, target, rel_tol=1e-12, abs_tol=1e-12),
                f"{series.name}: inconsistent {metric}")
    return result


def profile():
    resolved = SOURCE.resolve(strict=True)
    relative = resolved.relative_to(Path.cwd()).as_posix()
    data = resolved.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    require(relative == SOURCE.as_posix() and digest == SHA256, "Source identity mismatch")
    records = list(csv.reader(io.StringIO(data.decode("utf-8-sig"), newline=""),
                              delimiter=",", quotechar='"', strict=True))
    header, rows = records[0], records[1:]
    require(header == COLUMNS and len(rows) == 6, "Header or authorized six-record scope changed")
    require(all(len(row) == len(header) for row in rows), "Ragged record")

    frame = pd.read_csv(io.BytesIO(data), encoding="utf-8-sig", engine="c",
                        sep=",", header=0, quotechar='"', doublequote=True,
                        skipinitialspace=False, skip_blank_lines=False, on_bad_lines="error",
                        keep_default_na=False, na_values=[""], decimal=".")
    require(frame.shape == (len(rows), len(header)) and frame.columns.tolist() == header,
            "Independent CSV readers disagree")
    read_dtypes = frame.dtypes.astype(str).to_dict()
    time = pd.to_datetime(frame.timestamp, format=TIME_FORMAT, errors="coerce")
    invalid = {"timestamp": int((frame.timestamp.notna() & time.isna()).sum())}
    frame["timestamp"] = time
    missing = {col: sum(row[index] == "" for row in rows) for index, col in enumerate(header)}
    numeric = {}
    for index, col in enumerate(CHANNELS, start=1):
        values = pd.to_numeric(frame[col], errors="coerce")
        finite_count = sum(math.isfinite(v) for v in values.dropna())
        invalid[col] = len(rows) - missing[col] - finite_count
        require(invalid[col] == 0, f"Invalid numeric token or non-finite value in {col}")
        numeric[col] = summarize_numeric(values, [float(row[index]) for row in rows if row[index]])
        frame[col] = values
    require(invalid["timestamp"] == 0, "Invalid timestamp")
    require(frame.isna().sum().to_dict() == missing, "Missing counts disagree")
    reference_times = [datetime.strptime(row[0], TIME_FORMAT) for row in rows if row[0]]
    require(time.dropna().tolist() == reference_times, "Timestamp parsing mismatch")
    duplicates = int(frame.duplicated(keep="first").sum())
    require(duplicates == sum(n-1 for n in Counter(map(tuple, rows)).values()), "Duplicate mismatch")
    n = len(rows)
    channel_missing = sum(missing[c] for c in CHANNELS)
    unique = frame.nunique(dropna=True).to_dict()
    repeated_times = len(reference_times) - len(set(reference_times))
    quality = {
        "constant_columns": [col for col in header if unique[col] == 1],
        "all_null_columns": [col for col in header if missing[col] == n],
        "duplicate_rows": duplicates, "invalid_values": invalid,
        "other_confirmed_anomalies": {"repeated_nonmissing_timestamps_beyond_first": repeated_times},
    }
    structure = {
        "engine_unit": NA, "unique_units": NA, "cycle": NA, "cycle_range": NA,
        "health_label": NA, "rul": NA, "timestamp": "timestamp",
        "timestamp_unique_nonmissing": unique["timestamp"],
        "sensor_columns": CHANNELS, "sensor_count": len(CHANNELS),
        "sensor_count_basis": "Numeric telemetry fields, including load_pct; physical device count is unknown.",
        "sensor_missing_cells": channel_missing, "sensor_cells": n * len(CHANNELS),
        "sensor_missing_rate": channel_missing / (n * len(CHANNELS)),
        "sensor_missing_rate_per_column": {c: missing[c] / n for c in CHANNELS},
        "sensor_value_range": {c: [numeric[c]["minimum"], numeric[c]["maximum"]] for c in CHANNELS},
    }
    source = {"dataset_id": DATASET_ID, "filename": resolved.name, "resolved_path": relative,
              "source_file_sha256": digest, "size_bytes": len(data), "read_status": "READ_OK"}
    inventory = {
        "work_item_id": "M1_DATASET_PROFILE_6CSV_V1", "dataset_count": 1, "record_count": n,
        "scope": "RESEARCH Brain confirmed all six data records of this file constitute one dataset.",
        "record_locator": "1-based logical CSV record after the header, inclusive range 1 through 6.",
        "path_base": "repository root", "datasets": [source],
    }
    profile_data = {
        **source, "row_count": n, "column_count": len(header), "column_names": header,
        "read_csv_dtypes": read_dtypes, "column_dtypes": frame.dtypes.astype(str).to_dict(),
        "missing_count_per_column": missing, "duplicate_row_count": duplicates,
        "numeric_summary": numeric, "categorical_summary": NA,
        "data_quality_flags": quality, "structure_analysis": structure,
        "errors_or_warnings": [f"{duplicates} duplicate row(s) retained.",
                               f"{sum(missing.values())} missing cell(s) retained."],
    }
    require(resolved.read_bytes() == data, "Source changed during profiling")
    return inventory, profile_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    inventory, result = profile()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in [("dataset_inventory.json", inventory), ("dataset_profiles.json", [result])]:
        (args.output_dir / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n",
                                            encoding="utf-8")
    print(f"Python {platform.python_version()} / pandas {pd.__version__}")
    print(f"source={SOURCE.as_posix()} bytes={result['size_bytes']} sha256={result['source_file_sha256']}")
    print(f"datasets=1 rows={result['row_count']} columns={result['column_count']}")
    print(f"missing={sum(result['missing_count_per_column'].values())} duplicate_rows={result['duplicate_row_count']}")
    print("Checks passed: source identity and stable bytes, record scope, schema, shape, missingness,")
    print("timestamps, duplicates and every numeric statistic against independent standard-library calculations.")


if __name__ == "__main__":
    main()
