"""Local HTTP adapter for the accepted FD001 Gate C snapshot."""
import argparse
import json
from pathlib import Path
import re
import signal
import sys

from flask import Flask, Response, request
from werkzeug.exceptions import HTTPException
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[3]
GATE_C = ROOT / "outputs/M2_FD001_DATA_CONTRACT_V1/gate_c/PUBLIC_SAFE"
sys.path.insert(0, str(GATE_C))
import reference_query as contract

META = contract.METADATA
SOURCE_DIR = ROOT / "data/FD001"
HTTP_STATUS = {
    "INVALID_SPLIT": 400, "UNKNOWN_UNIT": 404, "UNKNOWN_SENSOR": 404,
    "CYCLE_OUT_OF_RANGE": 422, "SOURCE_NOT_VERIFIED": 503, "RUL_MAPPING_INVALID": 503,
}


def json_response(payload, status=200):
    try:
        body = json.dumps(payload, allow_nan=False, separators=(",", ":"))
    except ValueError:
        return web_error("NON_FINITE_RESULT", "Response contains a non-finite number.",
                         500, "REVALIDATE_RESULT")
    return Response(body, status=status, mimetype="application/json",
                    headers={"Cache-Control": "no-store"})


def web_error(code, message, http_status, recovery, **context):
    return json_response({"status": "error", "error": {
        "error_code": code, "message": message,
        "input_context": context, "recoverability": recovery,
    }}, http_status)


def contract_error(payload):
    return json_response({"status": "error", "error": payload}, HTTP_STATUS[payload["error_code"]])


class ParameterError(ValueError):
    def __init__(self, name, reason):
        super().__init__(reason)
        self.name = name


def parameters(*required):
    for name in request.args:
        if name not in required:
            raise ParameterError(name, "Unexpected parameter.")
    values = {}
    for name in required:
        items = request.args.getlist(name)
        if len(items) != 1 or not items[0]:
            raise ParameterError(name, "Provide exactly one nonempty value.")
        value = items[0]
        if name != "split":
            if not re.fullmatch(r"-?[0-9]+", value):
                raise ParameterError(name, "Expected a decimal integer.")
            try:
                value = int(value)
            except ValueError:
                raise ParameterError(name, "Integer exceeds parser limit.") from None
        values[name] = value
    return values


def success(data, sources, **context):
    provenance = {
        "contract_version": META["schema_version"],
        "verification_status": contract.RAW_VERIFIED,
        "sources": [{"source_filename": META["source_files"][s],
                     "source_sha256": META["source_sha256"][s]} for s in sources],
        **context,
    }
    return json_response({"status": "ok", "data": {"dataset_id": META["dataset_id"], **data},
                          "provenance": provenance})


def create_app(source_dir=SOURCE_DIR):
    app = Flask(__name__, static_folder=None)
    app.config["TRUSTED_HOSTS"] = ["127.0.0.1", "localhost"]
    failure = None
    try:
        snapshot = contract.FD001(source_dir)
    except contract.ContractError as exc:
        failure = exc.payload

    @app.before_request
    def check_snapshot():
        if failure is not None and request.url_rule is not None:
            return contract_error(failure)

    @app.errorhandler(contract.ContractError)
    def on_contract_error(exc):
        return contract_error(exc.payload)

    @app.errorhandler(ParameterError)
    def on_parameter_error(exc):
        return web_error("INVALID_PARAMETER", str(exc), 400, "CORRECT_INPUT", parameter=exc.name)

    @app.errorhandler(HTTPException)
    def on_http_error(exc):
        response = web_error("HTTP_ERROR", exc.name, exc.code, "CHECK_REQUEST")
        if exc.code == 405:
            response.headers["Allow"] = ", ".join(sorted(exc.valid_methods))
        return response

    @app.get("/api/health")
    def health():
        parameters()
        return success({"service": "ready"}, META["source_files"])

    @app.get("/api/catalog")
    def catalog():
        parameters()
        return success({"splits": META["available_splits"], **snapshot.sensors()},
                       META["source_files"], metadata_source="fd001_column_schema.json")

    @app.get("/api/units")
    def units():
        split = parameters("split")["split"]
        return success(snapshot.units(split), [split], split=split, column_name="unit_id",
                       column_position=1)

    @app.get("/api/history")
    def history():
        args = parameters("split", "unit", "sensor", "start", "end")
        split = args["split"]
        query = dict(split=split, unit_id=args["unit"], sensor_id=args["sensor"],
                     cycle_start=args["start"], cycle_end=args["end"])
        rows = snapshot.sensor(**query)
        keys = ("cycle", "value", "source_record_index", "source_physical_line", "column_position")
        points = [{k: row[k] for k in keys} for row in rows]
        return success({**query, "observation_count": len(points), "points": points}, [split],
                       **query, column_name=rows[0]["column_name"],
                       column_position=rows[0]["column_position"], index_base=1,
                       source_row_reference="/data/points", calculation_method="Direct source lookup")

    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal.default_int_handler)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    with make_server("127.0.0.1", args.port, create_app(args.source_dir)) as server:
        print(f"Listening at http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
