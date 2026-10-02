"""G0.42 — Audit signature per record (J-0.8.50).

Criterion: verify_chain() detects re-hash attacks.

The attack (from external red team, J-0.8.50):
  1. Modify a record's `data`.
  2. Recompute its `hash`.
  3. Recompute all subsequent hashes.
  4. Result: hash chain is intact, but content is forged.

Without signatures, verify_chain() returns OK. With per-record
signatures (V0.7.19), it must FAIL.

Scenarios:
  S1: New record has "sig" -> STRICT_VALID
  S2: Modify "data" without re-signing -> hash mismatch (early exit)
  S3: Modify "data" AND recompute hash -> sig invalid (must FAIL)
  S4: Missing "sig" at seq > cutoff -> STRICT_MISSING (must FAIL)
  S5: Legacy log (no sig) + cutoff_seq covering all -> ok=True,
      legacy_unverified=N (explicit, not silent)

Read-only: uses temp files, does NOT touch the real log.
"""
import json
import hashlib
import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "audit"))

import append_only_log as aol
import integrity as integ


def _hash_record(seq, ts, prev_hash, kind, data):
    payload = json.dumps(
        {"seq": seq, "ts": ts, "prev_hash": prev_hash, "kind": kind, "data": data},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _with_temp_log(fn):
    """Run fn with LOG_PATH patched. Returns fn's result."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False
    )
    tmp_path = Path(tmp.name)
    tmp.close()

    orig_aol = aol.LOG_PATH
    orig_integ = integ.LOG_PATH
    aol.LOG_PATH = tmp_path
    integ.LOG_PATH = tmp_path

    try:
        return fn(tmp_path)
    finally:
        aol.LOG_PATH = orig_aol
        integ.LOG_PATH = orig_integ
        if tmp_path.exists():
            tmp_path.unlink()


def check_1_new_record_has_sig():
    """S1: append() produces a record with 'sig'."""
    def run(tmp):
        rec = aol.append("test_kind", {"a": 1})
        return "sig" in rec and len(rec["sig"]) == 128  # 64 bytes hex
    return _with_temp_log(run)


def check_2_verify_chain_ok_on_new_log():
    """S1: verify_chain() returns ok with strict_valid > 0."""
    def run(tmp):
        aol.append("k1", {"a": 1})
        aol.append("k2", {"b": 2})
        result = integ.verify_chain(cutoff_seq=None)
        return (
            result.get("ok") is True
            and result.get("strict_valid") == 2
            and result.get("legacy_unverified") == 0
        )
    return _with_temp_log(run)


def check_3_data_tamper_detected():
    """S2: modifying 'data' without recomputing hash -> FAIL."""
    def run(tmp):
        aol.append("k1", {"a": 1})
        aol.append("k2", {"b": 2})
        # Tamper: change data of first record
        lines = tmp.read_text(encoding="utf-8").strip().split("\n")
        rec0 = json.loads(lines[0])
        rec0["data"] = {"a": 999}
        lines[0] = json.dumps(rec0, ensure_ascii=False, separators=(",", ":"))
        tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = integ.verify_chain(cutoff_seq=None)
        return result.get("ok") is False
    return _with_temp_log(run)


def check_4_rehash_attack_detected():
    """S3: THE ATTACK. Modify data + recompute hash + recompute subsequent.

    Without signatures, this would pass. With signatures, it must FAIL.
    """
    def run(tmp):
        aol.append("k1", {"a": 1})
        aol.append("k2", {"b": 2})
        aol.append("k3", {"c": 3})

        lines = tmp.read_text(encoding="utf-8").strip().split("\n")
        records = [json.loads(l) for l in lines]

        # Tamper record 0
        records[0]["data"] = {"a": 999}
        records[0]["hash"] = _hash_record(
            records[0]["seq"], records[0]["ts"],
            records[0]["prev_hash"], records[0]["kind"],
            records[0]["data"])

        # Recompute subsequent chain
        for i in range(1, len(records)):
            records[i]["prev_hash"] = records[i-1]["hash"]
            records[i]["hash"] = _hash_record(
                records[i]["seq"], records[i]["ts"],
                records[i]["prev_hash"], records[i]["kind"],
                records[i]["data"])
            # NOTE: sig is NOT recomputed (attacker has no key)

        tmp.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False,
                                 separators=(",", ":")) for r in records) + "\n",
            encoding="utf-8")

        result = integ.verify_chain(cutoff_seq=None)
        # The signature over f"{seq}|{hash}" is now invalid
        # because hash changed but sig did not.
        return result.get("ok") is False
    return _with_temp_log(run)


def check_5_missing_sig_strict_mode():
    """S4: a record without 'sig' in strict mode -> FAIL."""
    def run(tmp):
        aol.append("k1", {"a": 1})
        # Manually remove sig from the record
        lines = tmp.read_text(encoding="utf-8").strip().split("\n")
        rec = json.loads(lines[0])
        del rec["sig"]
        tmp.write_text(
            json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8")
        result = integ.verify_chain(cutoff_seq=None)
        return result.get("ok") is False
    return _with_temp_log(run)


def check_6_legacy_explicit():
    """S5: legacy log (no sig) + cutoff covers it -> ok with legacy count."""
    def run(tmp):
        # Build a synthetic legacy log (no sig) manually
        rec0 = {
            "seq": 0, "ts": "2026-01-01T00:00:00+00:00",
            "prev_hash": "0" * 64, "kind": "genesis",
            "data": {"legacy": True},
        }
        rec0["hash"] = _hash_record(
            rec0["seq"], rec0["ts"], rec0["prev_hash"],
            rec0["kind"], rec0["data"])
        tmp.write_text(
            json.dumps(rec0, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8")

        # With cutoff=0, this record is LEGACY_UNVERIFIED
        result = integ.verify_chain(cutoff_seq=0)
        return (
            result.get("ok") is True
            and result.get("legacy_unverified") == 1
            and result.get("strict_valid") == 0
        )
    return _with_temp_log(run)


def main():
    checks = [
        ("S1 new record has sig",         check_1_new_record_has_sig),
        ("S1 verify_chain ok on new",     check_2_verify_chain_ok_on_new_log),
        ("S2 data tamper detected",       check_3_data_tamper_detected),
        ("S3 re-hash attack detected",    check_4_rehash_attack_detected),
        ("S4 missing sig in strict",      check_5_missing_sig_strict_mode),
        ("S5 legacy explicit (cutoff)",   check_6_legacy_explicit),
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

    print("  Audit signature checks: {}/{}".format(passed, len(checks)))
    if failed:
        print("  FAILED: {}".format(failed))

    if passed == len(checks):
        print("G0.42: CLOSED ({}/{})".format(passed, len(checks)))
        return 0
    else:
        print("G0.42: FAILED ({}/{})".format(passed, len(checks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
