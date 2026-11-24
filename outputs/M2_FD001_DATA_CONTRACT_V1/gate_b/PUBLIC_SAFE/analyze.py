"""Run Gate B from the repository root with the three authorized FD001 TXT files."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import statistics
import sys

import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "gate_a" / "PUBLIC_SAFE"))
import validate as gate_a


REL_TOL = 1e-10
ABS_TOL = 1e-12
SENSORS = gate_a.COLUMNS[5:]
METHOD = "OLS with intercept; centered Cycle and Sensor covariance divided by centered Cycle sum of squares"


def save(directory, name, output):
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def check(evidence, name, expected, actual, method):
    if isinstance(expected, float):
        passed = isinstance(actual, (float, int)) and math.isclose(expected, actual, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    else:
        passed = expected == actual
    error = None if passed else "Independent results differ"
    evidence.append(dict(check_name=name, expected=expected, actual=actual,
                         status="PASS" if passed else "FAIL", error=error, method=method))
    if not passed:
        raise ValueError(f"{name}: {error}")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def parse_reference(path):
    """Read raw tokens, keeping logical record number separate from physical line."""
    with path.open("rb") as stream:
        for line_number, line in enumerate(stream, 1):
            fields = re.findall(rb"\S+", line)
            if fields:
                yield line_number, [field.decode("ascii") for field in fields]


def summary(values, reference, report, name):
    stats = dict(count=len(values), minimum=float(np.min(values)), maximum=float(np.max(values)),
                 mean=float(np.mean(values)), standard_deviation=float(np.std(values, ddof=1)))
    expected = dict(count=len(reference), minimum=min(reference), maximum=max(reference),
                    mean=statistics.mean(reference), standard_deviation=statistics.stdev(reference))
    for metric, target in expected.items():
        check(report, f"{name}.{metric}", target, stats[metric], "statistics and built-ins vs NumPy")
    return stats


def classify(distinct, count, total):
    if distinct == 1:
        return "CONSTANT"
    if distinct > 1 and count * 100 >= total * 99:
        return "NEAR_CONSTANT"
    return "VARIABLE"


def slopes(x, y):
    """Compute centered OLS for the finite paired observations."""
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 2:
        return None, "fewer than two valid observations"
    centered = x - x.mean()
    denominator = centered @ centered
    if denominator == 0:
        return None, "zero cycle variance"
    if np.min(y) == np.max(y):
        return 0.0, None
    return float(centered @ (y - y.mean()) / denominator), None


def reference_slope(cycles, values):
    pairs = [(x, y) for x, y in zip(cycles, values, strict=True) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return None, "fewer than two valid observations"
    x, y = zip(*pairs)
    if min(x) == max(x):
        return None, "zero cycle variance"
    return 0.0 if min(y) == max(y) else statistics.linear_regression(x, y).slope, None


def analyze(split, evidence):
    gate_a_checks = []
    inv, _, unit_info, _, _, data, _ = gate_a.inspect(split, gate_a_checks)
    path = gate_a.DATA / gate_a.FILES[split]
    parsed = list(parse_reference(path))
    tokens = [row for _, row in parsed]
    rows = [tuple(map(float, row)) for row in tokens]
    groups = defaultdict(list)
    for i, row in enumerate(tokens):
        groups[int(row[0])].append(i)
    check(evidence, f"{split}.record_count", len(rows), inv["valid_records"], "raw regex records vs Gate A")
    check(evidence, f"{split}.unit_count", len(groups), len(unit_info), "dictionary vs NumPy grouping")
    check(evidence, f"{split}.duplicate_records", len(rows)-len(set(rows)),
          len(data)-len(np.unique(data, axis=0)), "Python tuple set vs NumPy unique rows")
    duplicates = len(rows)-len(set(rows))
    key_duplicates = len(rows)-len({(row[0], row[1]) for row in rows})
    check(evidence, f"{split}.duplicate_cycle_keys", key_duplicates,
          len(data)-len(np.unique(data[:, :2], axis=0)), "Python tuple set vs NumPy unique keys")

    column_stats = {}
    for pos, name in enumerate(gate_a.COLUMNS):
        ref = [row[pos] for row in rows]
        col = data[:, pos]
        nan = sum(math.isnan(v) for v in ref)
        infinity = sum(math.isinf(v) for v in ref)
        # Whitespace delimits tokens. Short rows are rejected by Gate A.
        missing = sum(len(row) <= pos or row[pos].lower() in ("", "nan", "+nan", "-nan") for row in tokens)
        for label, expected, actual in [
            ("missing_count", missing, int(np.isnan(col).sum())),
            ("nan_count", nan, int(np.isnan(col).sum())),
            ("infinity_count", infinity, int(np.isinf(col).sum())),
            ("invalid_numeric_count", nan+infinity, int((~np.isfinite(col)).sum())),
        ]:
            check(evidence, f"{split}.{name}.{label}", expected, actual, "raw regex tokens and math vs NumPy masks")
        valid = [v for v in ref if math.isfinite(v)]
        values, counts = np.unique(col[np.isfinite(col)], return_counts=True)
        ref_counts = Counter(valid)
        highest = int(counts.max())
        check(evidence, f"{split}.{name}.distribution_counts", True,
              ref_counts == dict(zip(values.tolist(), counts.tolist())), "Counter vs NumPy unique with counts")
        status = classify(len(values), highest, len(valid))
        expected_status = ("CONSTANT" if len(ref_counts)==1 else
                           "NEAR_CONSTANT" if max(ref_counts.values())/len(valid)>=0.99 else "VARIABLE")
        check(evidence, f"{split}.{name}.variation_class", expected_status, status, "Counter ratio vs integer count threshold")
        stats = summary(col[np.isfinite(col)], valid, evidence, f"{split}.{name}")
        column_stats[name] = dict(**stats, missing_count=missing, missing_rate=missing/len(data),
                                  nan_count=nan, infinity_count=infinity, invalid_numeric_count=nan+infinity,
                                  distinct_count=len(values), dominant_count=highest,
                                  dominant_fraction=highest/len(valid), variation_class=status, physical_unit="UNKNOWN")
    quality = dict(row_count=len(rows), unit_count=len(groups),
                   observed_cycle_range=[int(data[:, 1].min()),int(data[:, 1].max())],
                   last_observed_cycle_range=[min(u["last_observed_cycle"] for u in unit_info),
                                              max(u["last_observed_cycle"] for u in unit_info)],
                   duplicate_records=duplicates, duplicate_unit_cycle_keys=key_duplicates,
                   missing_count=sum(c["missing_count"] for c in column_stats.values()),
                   missing_rate=sum(c["missing_count"] for c in column_stats.values())/data.size,
                   invalid_numeric_count=sum(c["invalid_numeric_count"] for c in column_stats.values()),
                   nan_count=sum(c["nan_count"] for c in column_stats.values()),
                   infinity_count=sum(c["infinity_count"] for c in column_stats.values()),
                   constant_columns=[c for c,s in column_stats.items() if s["variation_class"]=="CONSTANT"],
                   near_constant_columns=[c for c,s in column_stats.items() if s["variation_class"]=="NEAR_CONSTANT"],
                   all_units_contiguous_from_cycle_one=True, source_sha256=inv["sha256"], columns=column_stats)

    trends, public_examples, local_examples = [], [], []
    lines = gate_a.read_lines(path)
    for info in unit_info:
        unit = info["unit_id"]
        indices = groups[unit]
        cycles = [int(tokens[i][1]) for i in indices]
        check(evidence, f"{split}.unit_{unit}.continuity", True,
              cycles==list(range(1,info["last_observed_cycle"]+1)) and len(cycles)==info["cycle_count"],
              "raw token range comparison vs Gate A NumPy group count, order and gap checks")
        for sensor_id, sensor in enumerate(SENSORS, 1):
            pos = sensor_id+4
            xs, ys = data[indices,1], data[indices,pos]
            ref = [rows[i][pos] for i in indices]
            slope, reason = slopes(xs, ys)
            expected, expected_reason = reference_slope(cycles, ref)
            check(evidence, f"{split}.unit_{unit}.{sensor}.slope", expected, slope,
                  "statistics.linear_regression (constant shortcut) vs centered NumPy dot products")
            if reason or expected_reason:
                check(evidence, f"{split}.unit_{unit}.{sensor}.reason", expected_reason, reason, "independent OLS applicability")
            trends.append(dict(unit_id=unit,sensor_id=sensor_id,slope=slope,reason=reason))
            if unit!=min(groups) or sensor_id not in (1, 2):
                continue
            valid = np.isfinite(ys)
            metrics = summary(ys[valid], [v for v in ref if math.isfinite(v)], evidence, f"{split}.{sensor}.example")
            example = dict(dataset_id="FD001",split=split,unit_id=unit,sensor_id=sensor_id,
                           cycle_start=cycles[0],cycle_end=cycles[-1],observation_count=metrics.pop("count"),
                           missing_count=int(np.isnan(ys).sum()), **metrics,
                           trend_slope=slope if slope is not None else "NOT_APPLICABLE", slope_reason=reason,
                           slope_method=METHOD, sensor_unit="UNKNOWN", slope_unit="UNKNOWN / Cycle",
                           source_file_sha256=inv["sha256"], verification_status="PASS")
            refs = []
            for index, cycle in zip(indices, cycles, strict=True):
                physical, row = parsed[index]
                detail = dict(dataset_id="FD001",split=split,unit_id=unit,cycle=cycle,sensor_id=sensor_id,
                              column_name=sensor,column_position=pos+1,source_filename=inv["filename"],
                              source_sha256=inv["sha256"],source_record_index=index+1,source_physical_line=physical,
                              original_value=row[pos])
                refs.append(detail)
            # Align every example observation with the raw token and Gate A logical/physical index.
            good = all(lines[r["source_physical_line"]-1].split()[pos]==r["original_value"]
                       and float(r["original_value"])==data[r["source_record_index"]-1,pos]
                       and int(data[r["source_record_index"]-1,1])==r["cycle"]
                       and int(data[r["source_record_index"]-1,0])==unit for r in refs)
            check(evidence, f"{split}.{sensor}.all_example_records", True, good,
                  "independent binary-token and physical-line parse vs Gate A lines and matrix")
            for label, p in zip(("first", "middle", "last"), (0,len(refs)//2,len(refs)-1), strict=True):
                r = refs[p]
                located = gate_a.locate(split, lines, sensor, unit=unit, cycle=r["cycle"])
                check(evidence, f"{split}.{sensor}.locator_sample_{label}",
                      True, all(located[k]==v for k,v in r.items() if k!="sensor_id"),
                      "Gate A Raw Locator full fields vs binary-regex source record")
            public_examples.append(dict(**example, source_record_references=dict(
                lookup_key=["split","unit_id","cycle","sensor_id"], count=len(refs),
                locator="Gate A PUBLIC_SAFE/validate.py --locate; column_position=sensor_id+5")))
            local_examples.append(dict(**example,start_value=float(ys[0]),end_value=float(ys[-1]),
                                       source_record_references=refs))
    return quality, trends, public_examples, local_examples


def trend_summary(trends):
    result = {}
    for sensor_id, sensor in enumerate(SENSORS, 1):
        entries = [e for e in trends if e["sensor_id"]==sensor_id]
        valid = [e["slope"] for e in entries if e["slope"] is not None]
        result[sensor] = dict(unit_count=len(entries),applicable=len(valid),
                              not_applicable=len(entries)-len(valid),
                              minimum=min(valid,default=None),maximum=max(valid,default=None),
                              mean=statistics.mean(valid) if valid else None,
                              median=statistics.median(valid) if valid else None,
                              zero_slope_count=sum(x==0 for x in valid), slope_unit="UNKNOWN / Cycle")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"local_only"/"reproduced")
    args = parser.parse_args()
    evidence, quality, trends, public, private = [], {}, {}, {}, {}
    print(f"Python {platform.python_version()} / NumPy {np.__version__}")
    try:
        for split, name in gate_a.FILES.items():
            check(evidence, f"{split}.SHA256_before", gate_a.HASHES[split], digest(gate_a.DATA/name),
                  "hashlib.file_digest vs authorized Gate A SHA256")
        for split in ("train","test"):
            quality[split], trends[split], public[split], private[split] = analyze(split,evidence)
        for split, name in gate_a.FILES.items():
            check(evidence, f"{split}.SHA256_after", gate_a.HASHES[split], digest(gate_a.DATA/name),
                  "hashlib.file_digest vs authorized Gate A SHA256")
        for split in quality:
            q = quality[split]
            print(f"{split}: rows={q['row_count']} units={q['unit_count']} trends={len(trends[split])} missing={q['missing_count']} duplicates={q['duplicate_records']} examples={len(public[split])}")
        save(args.output,"data_quality_report.json",quality)
        save(args.output,"sensor_trend_summary.json",{s:trend_summary(v) for s,v in trends.items()})
        save(args.output,"trend_examples.json",public)
        save(args.output,"local_only/unit_sensor_slopes.json",trends)
        save(args.output,"local_only/trend_examples_full.json",private)
        print(f"Independent checks passed={len(evidence)}; all three source hashes unchanged")
    finally:
        save(args.output,"local_only/independent_checks_full.json",evidence)
        counts = Counter(("slope" if ".slope" in c["check_name"] else
                          "locator" if ".locator_sample_" in c["check_name"] or ".all_example_records" in c["check_name"] else
                          "continuity" if ".continuity" in c["check_name"] else
                          "other") for c in evidence if c["status"]=="PASS")
        save(args.output,"independent_checks.json",dict(
            total=len(evidence), passed=sum(counts.values()), failed=len(evidence)-sum(counts.values()),
            passed_by_category=counts, relative_tolerance=REL_TOL, absolute_tolerance=ABS_TOL,
            local_detail_fields=["check_name","expected","actual","status","error","method"]))


if __name__ == "__main__":
    main()
