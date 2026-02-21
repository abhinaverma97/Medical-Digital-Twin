#!/usr/bin/env python3
"""Simple integration smoke test for Teliport backend.
Uses only Python stdlib so it runs without extra deps.

Runs:
 - POST /requirements/ (adds a requirement)
 - POST /design/build
 - POST /simulation/run
 - POST /export/validate
 - GET  /export/traceability

Exit code: 0 on success, non-zero on failure.
"""
import json
import sys
import urllib.request
import urllib.error
from urllib.parse import urljoin

BASE = "http://127.0.0.1:8000/"

REQ_SAMPLE = {
    "id": "REQ-IT-001",
    "title": "Integration test requirement - pressure limit",
    "description": "Integration test: device must limit pressure to safe bound.",
    "parent_id": None,
    "type": "functional",
    "priority": "SHALL",
    "status": "Approved",
    "subsystem": "PressureControl",
    "parameter": "airway_pressure",
    "min_value": 0.0,
    "max_value": 30.0,
    "unit": "cmH2O",
    "tolerance": 1.0,
    "response_time_ms": 100,
    "interface": "PressureControl -> AlarmSystem",
    "protocol": "Analog",
    "hazard": "Excessive airway pressure",
    "severity": "High",
    "probability": "Occasional",
    "standard": "ISO 14971",
    "clause": "Risk assessment",
    "verification": {"method": "test", "description": "Bench test with test lung."}
}


def request(method, path, data=None, expect_json=True):
    url = urljoin(BASE, path)
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.getcode()
            raw = resp.read()
            text = raw.decode("utf-8") if raw else ""
            if expect_json and text:
                try:
                    return status, json.loads(text)
                except Exception:
                    return status, text
            return status, text
    except urllib.error.HTTPError as he:
        try:
            detail = he.read().decode()
        except Exception:
            detail = str(he)
        return he.code, detail
    except Exception as e:
        return None, str(e)


def fail(msg):
    print("FAIL:", msg)
    sys.exit(2)


def main():
    print("Posting sample requirement to /requirements/")
    status, resp = request("POST", "/requirements/", data=REQ_SAMPLE)
    print("->", status, resp)
    if status not in (200, 201):
        fail(f"adding requirement failed: {status} {resp}")

    print("Calling POST /design/build")
    status, resp = request("POST", "/design/build")
    print("->", status, resp)
    if status != 200:
        fail(f"design build failed: {status} {resp}")

    print("Calling POST /simulation/run")
    status, resp = request("POST", "/simulation/run")
    print("->", status, (resp if isinstance(resp, dict) else str(resp)[:200]))
    if status != 200:
        fail(f"simulation run failed: {status} {resp}")

    print("Calling POST /export/validate")
    status, resp = request("POST", "/export/validate")
    print("->", status, (resp if isinstance(resp, dict) else str(resp)[:200]))
    if status != 200:
        fail(f"export validate failed: {status} {resp}")

    print("Calling GET /export/traceability")
    status, resp = request("GET", "/export/traceability")
    print("->", status, ("<json>" if isinstance(resp, dict) or isinstance(resp, list) else str(resp)[:200]))
    if status != 200:
        fail(f"traceability failed: {status} {resp}")

    print("Integration smoke passed.")


if __name__ == '__main__':
    main()
