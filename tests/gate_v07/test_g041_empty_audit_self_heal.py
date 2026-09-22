"""G0.41 — Empty Audit Log Self-Healing.

Criterion:
  - Create an empty audit log file (temp)
  - Call audit.append() once
  - Verify it succeeds (no TypeError)
  - Verify the first record has seq == 1
  - Verify prev_hash == 64 zeros (genesis link)
  - Verify kind is preserved

This test guards against J-0.8.7 (empty audit.jsonl breaks
append).

Read-only. Uses a temp file, does not touch the real log.
"""
import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "audit"))

import append_only_log as aol

ZERO64 = "0" * 64


def _with_temp_log(fn):
    """Run fn with LOG_PATH and CKPT_PATH patched to temp files."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False
    )
    tmp_path = Path(tmp.name)
    tmp.close()

    orig_log = aol.LOG_PATH
    orig_ckpt = aol.CKPT_PATH
    tmp_ckpt = tmp_path.parent / (tmp_path.name + ".ckpt")

    aol.LOG_PATH = tmp_path
    aol.CKPT_PATH = tmp_ckpt

    try:
        return fn(tmp_path)
    finally:
        aol.LOG_PATH = orig_log
        aol.CKPT_PATH = orig_ckpt
        if tmp_path.exists():
            tmp_path.unlink()
        if tmp_ckpt.exists():
            tmp_ckpt.unlink()


def check_1_append_succeeds():
    """append() on an empty log must not raise."""
    def run(tmp):
        rec = aol.append("test_kind", {"a": 1})
        return isinstance(rec, dict) and rec.get("kind") == "test_kind"
    return _with_temp_log(run)


def check_2_first_seq_is_1():
    """First real record after synthetic genesis has seq == 1."""
    def run(tmp):
        rec = aol.append("test_kind", {"a": 1})
        return rec.get("seq") == 1
    return _with_temp_log(run)


def check_3_prev_hash_is_genesis():
    """First real record links to genesis (64 zeros)."""
    def run(tmp):
        rec = aol.append("test_kind", {"a": 1})
        return rec.get("prev_hash") == ZERO64
    return _with_temp_log(run)


def check_4_second_append_chains():
    """A second append links to the first record's hash."""
    def run(tmp):
        r1 = aol.append("k1", {"a": 1})
        r2 = aol.append("k2", {"b": 2})
        return (
            r2.get("seq") == 2
            and r2.get("prev_hash") == r1.get("hash")
        )
    return _with_temp_log(run)


def check_5_read_all_returns_two():
    """read_all() returns both real records (genesis is synthetic)."""
    def run(tmp):
        aol.append("k1", {"a": 1})
        aol.append("k2", {"b": 2})
        records = aol.read_all()
        return len(records) == 2
    return _with_temp_log(run)


def main():
    checks = [
        ("append succeeds on empty log", check_1_append_succeeds),
        ("first seq == 1", check_2_first_seq_is_1),
        ("prev_hash == genesis", check_3_prev_hash_is_genesis),
        ("second append chains", check_4_second_append_chains),
        ("read_all returns both", check_5_read_all_returns_two),
    ]

    passed = 0
    failed = []
    for name, fn in checks:
        try:
            ok = bool(fn())
        except Exception as e:
            ok = False
            print("  {}: EXCEPTION {}".format(name, e))
        if ok:
            passed += 1
        else:
            failed.append(name)

    print("  Empty-log self-healing checks: {}/{}".format(
        passed, len(checks)))
    if failed:
        print("  FAILED: {}".format(failed))

    if passed == len(checks):
        print("G0.41: CLOSED ({}/{})".format(passed, len(checks)))
        return 0
    else:
        print("G0.41: FAILED ({}/{})".format(passed, len(checks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
