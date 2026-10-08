"""G0.45 — Corrupted audit log fails loudly (J-0.8.62 corrected).

Criterion:
  audit.append() on a malformed log must raise a dedicated
  exception (CorruptedAuditLog), not a bare KeyError or
  JSONDecodeError. The error must identify the line and the
  missing field.

Scenarios:
  S1: Valid log -> _read_last() returns last record.
  S2: Malformed record {"seq":0} (no hash) -> CorruptedAuditLog.
  S3: Invalid JSON line -> CorruptedAuditLog.
  S4: Empty file -> synthetic genesis (unchanged, J-0.8.7).
  S5: append() on malformed log -> CorruptedAuditLog (not KeyError).

Read-only. Uses temp files, does NOT touch the real log.
"""
import json
import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "audit"))

import append_only_log as aol


def _with_temp_log(fn, content=None):
    """Run fn with LOG_PATH patched to a temp file.

    If content is provided, the temp file is pre-filled with it.
    """
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False
    )
    tmp_path = Path(tmp.name)
    if content is not None:
        tmp.write(content)
    tmp.close()

    orig = aol.LOG_PATH
    aol.LOG_PATH = tmp_path
    try:
        return fn(tmp_path)
    finally:
        aol.LOG_PATH = orig
        if tmp_path.exists():
            tmp_path.unlink()


def check_1_valid_log_read():
    """S1: valid log -> _read_last() returns last record."""
    def run(tmp):
        aol.append("k1", {"a": 1})
        aol.append("k2", {"b": 2})
        last = aol._read_last()
        return last["seq"] == 2 and "hash" in last
    return _with_temp_log(run)


def check_2_missing_hash_raises():
    """S2: record without 'hash' -> CorruptedAuditLog."""
    def run(tmp):
        try:
            aol._read_last()
            return False
        except Exception as e:
            return type(e).__name__ == "CorruptedAuditLog"
    return _with_temp_log(run, content='{"seq":0}\n')


def check_3_invalid_json_raises():
    """S3: invalid JSON -> CorruptedAuditLog."""
    def run(tmp):
        try:
            aol._read_last()
            return False
        except Exception as e:
            return type(e).__name__ == "CorruptedAuditLog"
    return _with_temp_log(run, content='not json at all\n')


def check_4_empty_file_synthetic():
    """S4: empty file -> synthetic genesis (J-0.8.7 unchanged)."""
    def run(tmp):
        last = aol._read_last()
        return last.get("kind") == "genesis_synthetic"
    return _with_temp_log(run, content="")


def check_5_append_on_malformed_raises():
    """S5: append() on malformed log -> CorruptedAuditLog, not KeyError."""
    def run(tmp):
        try:
            aol.append("k", {})
            return False
        except KeyError:
            return False  # bare KeyError is the old, bad behavior
        except Exception as e:
            return type(e).__name__ == "CorruptedAuditLog"
    return _with_temp_log(run, content='{"seq":0}\n')


def main():
    checks = [
        ("S1 valid log read",              check_1_valid_log_read),
        ("S2 missing hash raises",         check_2_missing_hash_raises),
        ("S3 invalid JSON raises",         check_3_invalid_json_raises),
        ("S4 empty file synthetic",        check_4_empty_file_synthetic),
        ("S5 append on malformed raises",  check_5_append_on_malformed_raises),
    ]

    passed = 0
    failed = []
    for name, fn in checks:
        try:
            ok = bool(fn())
        except Exception as e:
            ok = False
            print("  {}: EXCEPTION {}: {}".format(name, type(e).__name__, e))
        if ok:
            passed += 1
        else:
            failed.append(name)

    print("  Corrupted-audit checks: {}/{}".format(passed, len(checks)))
    if failed:
        print("  FAILED: {}".format(failed))

    if passed == len(checks):
        print("G0.45: CLOSED ({}/{})".format(passed, len(checks)))
        return 0
    else:
        print("G0.45: FAILED ({}/{})".format(passed, len(checks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
