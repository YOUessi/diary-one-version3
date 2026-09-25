"""Run existing tests against the packaged source with socket use prohibited."""
import hashlib
import io
import json
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "handoffs/codex_app_20260904_r1"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACKAGE / "source/src"))


def no_socket(*args, **kwargs):
    raise PermissionError("offline handoff regression: socket operation forbidden")


def main():
    with patch.object(socket.socket, "bind", no_socket), patch.object(socket.socket, "connect", no_socket), patch.object(socket.socket, "connect_ex", no_socket):
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    evidence = {
        "source": "PACKAGED_SOURCE_WITH_EXISTING_REPOSITORY_TESTS",
        "python": sys.version, "tests_run": result.testsRun,
        "passed": result.testsRun - len(result.skipped) - len(result.failures) - len(result.errors),
        "failures": len(result.failures), "errors": len(result.errors),
        "skips": [{"test": test.id(), "reason": reason} for test, reason in result.skipped],
        "network_and_listening_socket_prohibited": True,
        "real_fixtures_read_locally_not_included_in_handoff": True,
        "test_inputs": [{"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in sorted((ROOT / "tests").rglob("*"))
                        if path.is_file() and path.suffix in (".py", ".json")],
    }
    if not result.wasSuccessful():
        print(stream.getvalue())
        raise SystemExit("regression failed; not recording a pass")
    (PACKAGE / "codex_regression_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: evidence[key] for key in ("tests_run", "passed", "failures", "errors", "skips")}))


if __name__ == "__main__":
    main()
