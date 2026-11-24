"""Validate FD001 contracts against the approved local files and Gate A/B evidence."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
import reference_query as query

HERE = Path(__file__).resolve().parent
M2 = HERE.parents[1]
A = M2 / "gate_a" / "PUBLIC_SAFE"
B = M2 / "gate_b" / "PUBLIC_SAFE"
DATA = Path("data/FD001")


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(directory, name, value):
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def raw_rows(source):
    """Independent binary line iterator and regex tokenizer."""
    path = DATA / query.METADATA["source_files"][source]
    with path.open("rb") as stream:
        rows = [(i, re.findall(rb"\S+", line)) for i, line in enumerate(stream, 1)]
    return [(i, fields) for i, fields in rows if fields]


def hash_sources():
    hashes = {}
    for split, name in query.METADATA["source_files"].items():
        with (DATA / name).open("rb") as stream:
            hashes[split] = hashlib.file_digest(stream, "sha256").hexdigest()
    return hashes


def require_fields(object_, fields):
    return set(fields) <= object_.keys()


def same_float(a, b):
    return math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12)


def gate_a_lookup(*args):
    result = subprocess.run([sys.executable, str(A/"validate.py"), *args],
                            check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def validate(out):
    checks, public, private = [], {}, {}

    def check(name, passed, method):
        checks.append(dict(check_name=name, status="PASS" if passed else "FAIL", method=method))
        if not passed:
            raise ValueError(f"Contract validation failed: {name}")

    def error_case(name, code, call):
        try:
            call()
        except query.ContractError as exc:
            envelope = exc.payload
            private.setdefault("errors", {})[name] = envelope
            check(name, envelope["error_code"] == code and set(envelope) == set(error_spec["error_envelope"])
                  and envelope["message"] == error_spec["errors"][code]["message"]
                  and envelope["recoverability"] == error_spec["errors"][code]["recoverability"],
                  f"Expected {code} and complete error envelope")
        else:
            check(name, False, f"Expected {code}")

    meta = json_file(HERE/"fd001_data_contract.json")
    schema = json_file(HERE/"fd001_column_schema.json")
    error_spec = json_file(HERE/"fd001_error_contract.json")
    check("JSON metadata, schema and error contract versions",
          meta["schema_version"]==schema["schema_version"]==error_spec["schema_version"]=="1.0.0",
          "Strict JSON decode and 3 document version comparison")
    check("metadata required keys", require_fields(meta, [
        "dataset_name","dataset_version","schema_version","source_files","source_sha256",
        "available_splits","row_counts","unit_counts","sensor_count","verification_status","verification_basis"]),
        "Contract keys")
    prior = json_file(A/"raw_schema.json")
    a_inventory = json_file(A/"file_inventory.json")
    check("source pins and row-count metadata agree with Gate A",
          all((meta["source_files"][s],meta["source_sha256"][s],meta["row_counts"][s]) ==
              (v["filename"],v["sha256"],v["valid_records"]) for s,v in a_inventory.items()),
          "Gate A accepted inventory vs Gate C contract")
    columns = schema["columns"]
    check("affinity and schema fields", schema["applies_to"]==meta["available_splits"]==["train","test"]
          and all(require_fields(c, ("column_name","column_position","dtype","semantic_role",
              "unit_of_measure_if_known","nullable","source_field")) for c in columns+schema["rul_columns"])
          and ["integer" if i<2 else "number" for i in range(26)]==[c["dtype"] for c in columns],
          "Required column fields and logical types")
    check("column positions and Train/Test schema",
          [(c["column_name"],c["column_position"]) for c in columns] ==
          [(c["name"],c["position"]) for c in prior["train"]] ==
          [(c["name"],c["position"]) for c in prior["test"]]
          and [(c["column_name"],c["column_position"]) for c in schema["rul_columns"]] ==
              [(c["name"],c["position"]) for c in prior["rul"]]
          and all(c["column_position"]==c["source_field"] for c in columns+schema["rul_columns"]),
          "Gate A accepted schema cross-check")
    before = hash_sources()
    check("source SHA-256 before execution", before==meta["source_sha256"], "Independent streaming file hash")
    fd = query.FD001(DATA)
    check("sensor listing and 1-based mapping", len(fd.sensors()["sensors"])==meta["sensor_count"]==21
          and [(s["sensor_id"],s["column_position"]) for s in fd.sensors()["sensors"]]==
              [(i,i+5) for i in range(1,22)], "API vs physical schema offsets")

    raw_test_units = {}
    gate_b = json_file(B/"trend_examples.json")
    for split in ("train","test"):
        raw = raw_rows(split)
        groups = {}
        for index, (line, tokens) in enumerate(raw, 1):
            unit, cycle = int(tokens[0]), int(tokens[1])
            groups.setdefault(unit, {})[cycle] = (index,line,tokens)
        check(f"{split} observed units", fd.units(split)["unit_ids"]==sorted(groups)
              and len(groups)==meta["unit_counts"][split], "Binary regex and independent grouping vs API")
        check(f"{split} all unit boundaries and locators", all(
            (u["first_cycle"],u["last_observed_cycle"],u["cycle_count"],
             u["source_locator"]["first"]["source_record_index"],u["source_locator"]["last"]["source_physical_line"])
            == (min(cycles),max(cycles),len(cycles),cycles[min(cycles)][0],cycles[max(cycles)][1])
            and require_fields(u, meta["operations"]["unit"]["output"])
            for unit,cycles in groups.items() for u in [fd.unit(split,unit)]),
            "All Units grouped from binary raw lines")
        unit = 1
        sensor_id = 2
        unit_cycles = groups[unit]
        first, last = min(unit_cycles), max(unit_cycles)
        result = fd.sensor(split,unit,sensor_id,first,last)
        position = sensor_id+5
        check(f"{split} inclusive sensor samples", [r["cycle"] for r in result]==sorted(unit_cycles) and all(
            (r["source_record_index"],r["source_physical_line"],r["value"],r["column_position"],
             r["source_filename"],r["source_sha256"]) ==
            (row[0],row[1],float(row[2][position-1]),position,meta["source_files"][split],before[split])
            and require_fields(r,meta["operations"]["sensor"]["output_item"])
            and require_fields(r["evidence"],meta["evidence"]["required"])
            for r in result for row in [unit_cycles[r["cycle"]]]),
            "All sample records reconciled against independent raw tokens")
        sample = result[0]
        found = gate_a_lookup("--locate",split,"--unit",str(unit),"--cycle",str(first),
                              "--column",sample["column_name"])
        check(f"{split} Gate A raw locator", all(sample[k]==found[k] for k in
              ("source_record_index","source_physical_line","source_filename","source_sha256","column_position"))
              and float(found["original_value"])==sample["value"],
              "Accepted locator CLI vs Gate C direct read")
        trend = fd.trend(split,unit,sensor_id,first,last)
        expected = next(r for r in gate_b[split] if r["unit_id"]==unit and r["sensor_id"]==sensor_id)
        check(f"{split} Gate B trend reproduction", trend["observation_count"]==expected["observation_count"]
              and trend["missing_count"]==expected["missing_count"]
              and all(same_float(trend[k],expected[k]) for k in
                      ("minimum","maximum","mean","standard_deviation","trend_slope"))
              and len(trend["evidence"]["source_row_reference"])==len(result)
              and require_fields(trend["evidence"],meta["evidence"]["required"]),
              "Gate B accepted NumPy OLS and statistics vs Python statistics")
        one = fd.trend(split,unit,sensor_id,first,first)
        check(f"{split} single-cycle boundary", one["observation_count"]==1
              and one["trend_slope"]=="NOT_APPLICABLE" and bool(one["slope_reason"]),
              "Inclusive single-cycle query with explicit OLS applicability")
        check(f"{split} constant slope", fd.trend(split,unit,1,first,last)["trend_slope"]==0.0,
              "Gate B constant Sensor 1 reproduced")
        private[split] = dict(unit=fd.unit(split,unit), sensor_rows=result, trend=trend, locator=found)
        public[split] = dict(dataset_id="FD001",split=split,unit_id=unit,sensor_id=sensor_id,
                             cycle_start=first,cycle_end=last,verified_observations=len(result),
                             source_filename=meta["source_files"][split], source_sha256=before[split],
                             verification_status="PASS", trend_slope=trend["trend_slope"])
        if split=="test":
            raw_test_units = groups

    rul_rows = raw_rows("rul")
    check("all RUL rank mappings", len(rul_rows)==len(raw_test_units)==100 and all(
          (r["rul_source_record_index"],r["rul_at_last_observation"],r["last_observed_cycle"],
           r["mapping_basis"],r["verification_status"],r["source_sha256"])
          == (i,int(rul_rows[i-1][1][0]),max(raw_test_units[u]),"MW_FD001_SORTED_ID",
              "VERIFIED_BY_REFERENCE_CONVENTION",before["rul"])
          and require_fields(r,meta["operations"]["rul"]["output"])
          for i,u in enumerate(sorted(raw_test_units),1) for r in [fd.rul("test",u)]),
          "Independently sorted Unit IDs and binary RUL record sequence vs query API")
    check("RUL mapping convention agrees with accepted Gate A",
          meta["rul"]["mapping_basis"]==json_file(A/"rul_mapping_spec.json")["basis_id"]
          and not meta["rul"]["native_unit_key"], "Accepted format convention comparison")
    sample_rul = fd.rul("test",1)
    lookup_rul = gate_a_lookup("--locate","rul","--record",str(sample_rul["rul_source_record_index"]))
    check("RUL value source locator", int(lookup_rul["original_value"])==sample_rul["rul_at_last_observation"]
          and lookup_rul["source_sha256"]==sample_rul["source_sha256"],
          "Accepted locator reads RUL raw record and SHA-256")
    private["rul"] = [fd.rul("test",u) for u in sorted(raw_test_units)]
    public["rul"] = {k:v for k,v in sample_rul.items() if k!="rul_at_last_observation"}
    public["evidence"] = {
        **{k:v for k,v in private["train"]["sensor_rows"][0]["evidence"].items() if k!="source_row_reference"},
        "source_row_reference":{"index_base":1,"column_position":7,
                                "locator_key":{"split":"train","unit_id":1,"cycle":1,"sensor_id":2},
                                "matched_physical_line_and_record_index":True},
    }

    error_case("INVALID_SPLIT","INVALID_SPLIT",lambda: fd.units("rul"))
    error_case("train RUL unavailable","INVALID_SPLIT",lambda: fd.rul("train",1))
    error_case("UNKNOWN_UNIT","UNKNOWN_UNIT",lambda: fd.unit("train",0))
    error_case("UNKNOWN_SENSOR","UNKNOWN_SENSOR",lambda: fd.sensor("test",1,22,1,1))
    error_case("CYCLE_OUT_OF_RANGE","CYCLE_OUT_OF_RANGE",lambda: fd.sensor("test",1,2,1,32))
    error_case("inverted cycle range","CYCLE_OUT_OF_RANGE",lambda: fd.sensor("train",1,2,2,1))
    # Exercise error paths while keeping original source bytes unchanged.
    with patch.dict(query.METADATA["source_sha256"], {"train":"0"*64}):
        error_case("SOURCE_NOT_VERIFIED","SOURCE_NOT_VERIFIED",lambda: query.FD001(DATA))
    valid_read = query.verified_records
    def incomplete_rul(directory, split):
        rows = valid_read(directory, split)
        return rows[:-1] if split=="rul" else rows
    with patch.object(query,"verified_records",incomplete_rul):
        error_case("RUL_MAPPING_INVALID","RUL_MAPPING_INVALID",lambda: query.FD001(DATA))

    cli = [sys.executable,str(HERE/"reference_query.py")]
    result = subprocess.run(cli+["sensor","test","1","2","1","1"],capture_output=True,text=True)
    check("CLI sensor JSON and exit code", result.returncode==0 and json.loads(result.stdout)==fd.sensor("test",1,2,1,1),
          "Actual subprocess and local API parity")
    result = subprocess.run(cli+["units","wrong"],capture_output=True,text=True)
    check("CLI error JSON and exit code", result.returncode==2 and json.loads(result.stdout)["error_code"]=="INVALID_SPLIT",
          "Actual subprocess structured error")
    check("source SHA-256 after execution", hash_sources()==before, "Independent streaming file hash")
    save(out,"fd001_verified_examples.json",public)
    save(out,"fd001_contract_validation.json",dict(schema_version=meta["schema_version"],source_sha256=before,
          total=len(checks),passed=len(checks),failed=0,checks=checks,worker_validation="PASS"))
    save(out,"local_only/complete_query_evidence.json",private)
    print(f"{len(checks)} checks passed; Train/Test sensor and trend, 100 RUL mappings, 6 error codes, source hashes stable")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=HERE.parent/"local_only"/"reproduced")
    args = parser.parse_args()
    print(f"Python {platform.python_version()} / NumPy {__import__('numpy').__version__} (Gate A locator only) / schema {query.METADATA['schema_version']}")
    validate(args.output)


if __name__=="__main__":
    main()
