"""Loopback HTTP tests with a source oracle independent of the Gate C adapter."""
from contextlib import contextmanager, ExitStack
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
from tempfile import mkdtemp, TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler, Request

from jsonschema import Draft202012Validator
from werkzeug.serving import make_server

HERE = Path(__file__).resolve().parent
PRIVATE = HERE / "local_only"
sys.path.insert(0, str(HERE.parent / "backend"))
import api

TRAIN = "/api/history?split=train&unit=1&sensor=7&start=1&end=20"
TEST = "/api/history?split=test&unit=2&sensor=7&start=3&end=5"
HTTP = build_opener(ProxyHandler({}))


@contextmanager
def serving(app):
    with make_server("127.0.0.1", 0, app) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            thread.join()


def reject_nonfinite(_):
    raise ValueError("Non-finite JSON token")


def request_json(base, path, method="GET"):
    try:
        response = HTTP.open(Request(base + path, method=method), timeout=10)
    except HTTPError as exc:
        response = exc
    with response:
        if response.headers.get_content_type() != "application/json":
            raise AssertionError("Expected JSON response")
        return response.status, json.loads(response.read(), parse_float=Decimal,
                                           parse_constant=reject_nonfinite)


def source_rows(split, unit, sensor, start, end):
    filename = f"{split}_FD001.txt"
    path = HERE.parents[2] / "data/FD001" / filename
    position = 5 + sensor
    digest = sha256()
    selected = []
    record = 0
    with path.open("rb") as stream:
        for physical_line, line in enumerate(stream, 1):
            digest.update(line)
            tokens = re.findall(rb"\S+", line)
            if not tokens:
                continue
            record += 1
            engine, cycle = map(int, tokens[:2])
            if engine == unit and start <= cycle <= end:
                selected.append(dict(cycle=cycle, value=Decimal(tokens[position - 1].decode("ascii")),
                                     source_record_index=record, source_physical_line=physical_line,
                                     column_position=position))
    return filename, digest.hexdigest(), selected


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PRIVATE.mkdir(exist_ok=True)
        cls.evidence = Path(mkdtemp(prefix="api-", dir=PRIVATE))
        cls.schemas = {}
        for kind in ("success", "error"):
            schema = json.loads((HERE.parent / "docs" / f"{kind}.schema.json").read_text())
            Draft202012Validator.check_schema(schema)
            cls.schemas[kind] = Draft202012Validator(schema)
        stack = ExitStack()
        cls.addClassCleanup(stack.close)
        port = os.environ.get("FD001_TEST_PORT")
        cls.base = (f"http://127.0.0.1:{int(port)}" if port
                    else stack.enter_context(serving(api.create_app())))

    def fetch(self, path, expected=200, base=None, method="GET"):
        status, body = request_json(base or self.base, path, method)
        self.assertEqual(status, expected)
        schema = self.schemas["success" if status == 200 else "error"]
        # Report only schema paths on failure, since payloads can contain telemetry.
        error = next(schema.iter_errors(body), None)
        self.assertIsNone(None if error is None else list(error.absolute_schema_path))
        return body

    def error(self, path, status, code, **options):
        error = self.fetch(path, status, **options)["error"]
        self.assertEqual(error["error_code"], code)
        if code in api.contract.ERRORS:
            for field in ("message", "recoverability"):
                self.assertEqual(error[field], api.contract.ERRORS[code][field])
        return error["input_context"]

    def test_health(self):
        body = self.fetch("/api/health")
        self.assertEqual(body["data"], {
            "dataset_id": "FD001",
            "schema_version": "1.0.0",
            "service": "ready",
            "source_verified": True,
            "source_status": "VERIFIED_LOCAL_SOURCE",
            "read_only": True,
        })
        self.assertIs(body["data"]["source_verified"], True)
        self.assertIs(body["data"]["read_only"], True)
        self.assertEqual(body["data"]["source_status"], body["provenance"]["verification_status"])
        pins = {s["source_filename"]: s["source_sha256"] for s in body["provenance"]["sources"]}
        for name in ("train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"):
            self.assertEqual(pins[name], sha256((api.SOURCE_DIR / name).read_bytes()).hexdigest())

    def test_catalog(self):
        data = self.fetch("/api/catalog")["data"]
        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertEqual(data["available_splits"], ["train", "test"])
        self.assertEqual(data["source_version"], api.META["dataset_version"])
        sensors = data["sensor_catalog"]
        expected = [column for column in api.contract.SCHEMA["columns"] if "sensor_id" in column]
        self.assertEqual(sensors, expected)
        self.assertEqual(len(sensors), 21)
        self.assertEqual(data["sensor_count"], len(sensors))
        self.assertEqual(data["splits"], data["available_splits"])
        self.assertEqual(data["sensors"], sensors)
        self.assertEqual([(s["sensor_id"], s["column_name"], s["column_position"], s["source_field"])
                          for s in sensors], [(i, f"sensor_{i}", i + 5, i + 5) for i in range(1, 22)])

    def check_units(self, split):
        body = self.fetch("/api/units?split=" + split)
        self.assertEqual(body["data"]["split"], split)
        self.assertEqual(body["data"]["unit_ids"], list(range(1, 101)))
        self.assertEqual(body["data"]["unit_count"], len(body["data"]["unit_ids"]))
        self.assertEqual(body["provenance"]["sources"][0]["source_filename"], f"{split}_FD001.txt")

    def test_train_units(self):
        self.check_units("train")

    def test_test_units(self):
        self.check_units("test")

    def reject_invalid_fields(self, path, wrong_types):
        body = self.fetch(path)
        schema = self.schemas["success"]
        for field, wrong_type in wrong_types.items():
            data = body["data"]
            with self.subTest(field=field, case="missing"):
                candidate = {**body, "data": {key: value for key, value in data.items() if key != field}}
                self.assertFalse(schema.is_valid(candidate))
            for case, value in (("wrong type", wrong_type), ("null", None)):
                with self.subTest(field=field, case=case):
                    candidate = {**body, "data": {**data, field: value}}
                    self.assertFalse(schema.is_valid(candidate))

    def test_health_schema_required_fields(self):
        self.reject_invalid_fields("/api/health", {
            "schema_version": 1, "source_verified": "true", "source_status": False, "read_only": 1,
        })

    def test_catalog_schema_required_fields(self):
        self.reject_invalid_fields("/api/catalog", {
            "schema_version": 1, "available_splits": "train", "sensor_catalog": {},
            "sensor_count": "21", "source_version": [],
        })

    def test_units_schema_required_fields(self):
        for split in ("train", "test"):
            with self.subTest(split=split):
                self.reject_invalid_fields(f"/api/units?split={split}", {"unit_count": "100"})

    def compare_history(self, path, split, unit, sensor, start, end):
        body = self.fetch(path)
        data, prov = body["data"], body["provenance"]
        query = dict(split=split, unit_id=unit, sensor_id=sensor, cycle_start=start, cycle_end=end)
        for name, value in query.items():
            self.assertEqual(data[name], value)
            self.assertEqual(prov[name], value)
        filename, digest, expected = source_rows(split, unit, sensor, start, end)
        self.assertEqual(prov["sources"], [dict(source_filename=filename, source_sha256=digest)])
        self.assertEqual(prov["column_name"], f"sensor_{sensor}")
        self.assertEqual(prov["column_position"], sensor + 5)
        self.assertEqual(prov["source_row_reference"], "/data/points")
        points = data["points"]
        self.assertEqual([r["cycle"] for r in points], list(range(start, end + 1)))
        self.assertEqual((len(expected), data["observation_count"]), (len(points), len(points)))
        comparison = []
        for source, actual in zip(expected, points, strict=True):
            match = source == actual
            comparison.append(dict(source=source, api=actual, exact_match=match))
        evidence = dict(query=query, provenance=prov, absolute_tolerance=0, relative_tolerance=0,
                        comparisons=comparison)
        (self.evidence / f"{split}.json").write_text(
            json.dumps(evidence, indent=2, default=str, allow_nan=False), encoding="utf-8")
        self.assertTrue(all(row["exact_match"] for row in comparison), "Source/API mismatch")

    def test_train_history_20_rows(self):
        self.compare_history(TRAIN, "train", 1, 7, 1, 20)

    def test_test_history(self):
        self.compare_history(TEST, "test", 2, 7, 3, 5)

    def test_missing_parameters(self):
        for name in ("split=train", "unit=1", "sensor=7", "start=1", "end=20"):
            path, query = TRAIN.split("?")
            incomplete = "&".join(field for field in query.split("&") if field != name)
            with self.subTest(field=name):
                context = self.error(path + "?" + incomplete, 400, "INVALID_PARAMETER")
                self.assertEqual(context["parameter"], name.split("=")[0])

    def test_malformed_parameters(self):
        for path in (TRAIN + "&sensor=8", TRAIN + "&extra=1", TRAIN.replace("unit=1", "unit="),
                     TRAIN.replace("start=1", "start=1.5")):
            self.error(path, 400, "INVALID_PARAMETER")

    def test_invalid_split(self):
        self.error(TRAIN.replace("train", "rul"), 400, "INVALID_SPLIT")

    def test_unknown_unit(self):
        self.error(TRAIN.replace("unit=1", "unit=101"), 404, "UNKNOWN_UNIT")

    def test_unknown_sensor(self):
        self.error(TRAIN.replace("sensor=7", "sensor=22"), 404, "UNKNOWN_SENSOR")

    def test_cycle_out_of_range(self):
        self.error(TRAIN.replace("end=20", "end=99999"), 422, "CYCLE_OUT_OF_RANGE")

    def test_inverted_range(self):
        self.error(TRAIN.replace("start=1", "start=21"), 422, "CYCLE_OUT_OF_RANGE")

    def test_missing_and_mismatched_source(self):
        with TemporaryDirectory(dir=PRIVATE) as directory:
            for mode in ("missing", "mismatch"):
                if mode == "mismatch":
                    (Path(directory) / "train_FD001.txt").write_bytes(b"invalid fixture")
                with self.subTest(mode=mode), serving(api.create_app(directory)) as base:
                    for path in ("/api/health", "/api/catalog", "/api/units?split=train", TRAIN):
                        context = self.error(path, 503, "SOURCE_NOT_VERIFIED", base=base)
                        self.assertEqual(context["source_filename"], "train_FD001.txt")

    def test_rul_mapping_error(self):
        original = api.contract.map_rul
        with patch.object(api.contract, "map_rul", lambda ids, rows: original(ids, rows[:-1])):
            with serving(api.create_app()) as base:
                context = self.error("/api/health", 503, "RUL_MAPPING_INVALID", base=base)
                self.assertEqual(context["rul_records"], 99)

    def test_nonfinite_serialization(self):
        app = api.create_app()
        original = api.contract.FD001.sensor
        with serving(app) as base:
            for value in (float("nan"), float("inf"), -float("inf")):
                def invalid_result(snapshot, **query):
                    rows = original(snapshot, **query)
                    rows[0]["value"] = value
                    return rows
                with patch.object(api.contract.FD001, "sensor", invalid_result):
                    self.error(TRAIN, 500, "NON_FINITE_RESULT", base=base)

    def test_read_only_routes(self):
        self.error(TRAIN, 405, "HTTP_ERROR", method="POST")
        self.error("/api/unknown", 404, "HTTP_ERROR")


if __name__ == "__main__":
    unittest.main(verbosity=2)
