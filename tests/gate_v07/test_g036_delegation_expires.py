"""G0.36 — Delegation Expires (H24 part 2).

Criterion: 5/5 expired delegations are denied.

For each:
  - Create delegation with short TTL
  - Verify it works before expiry
  - Wait for expiry
  - Verify it is denied after expiry

Read-only. Does NOT modify V0.5 or V0.6 files.
"""
import sys
import time
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.delegation import (
    Delegation, DelegationRegistry,
)

N_TESTS = 5
TTL = 0.05  # 50 ms


def _test_one(i):
    """Return True if expiry is correctly enforced."""
    reg = DelegationRegistry()

    action = "file_read" if i % 2 == 0 else "compute_add"
    grantee = "file_agent_1" if i % 2 == 0 else "compute_agent_1"

    d = Delegation(
        granter_id="owner",
        grantee_id=grantee,
        scope=[action],
        ttl_seconds=TTL,
    )
    reg.register(d)

    # 1. Before expiry: allowed
    ok, _ = reg.is_allowed(grantee, action)
    if not ok:
        return False, "not allowed before expiry"

    # 2. Wait for expiry
    time.sleep(TTL + 0.05)

    # 3. Expired
    if not d.is_expired():
        return False, "not expired after ttl"

    # 4. After expiry: denied
    ok, reason = reg.is_allowed(grantee, action)
    if ok:
        return False, "allowed after expiry"

    # 5. is_valid also False
    if d.is_valid():
        return False, "is_valid True after expiry"

    # 6. Not revoked
    if d.is_revoked():
        return False, "wrongly marked as revoked"

    return True, None


def main():
    passed = 0
    failed = []
    for i in range(N_TESTS):
        try:
            ok, msg = _test_one(i)
        except Exception as e:
            ok = False
            msg = "{}: {}".format(type(e).__name__, e)
        if ok:
            passed += 1
        else:
            failed.append((i, msg))

    print("  Expired delegations denied: {}/{}".format(passed, N_TESTS))
    if failed:
        for i, m in failed[:5]:
            print("    test {}: {}".format(i, m))

    if passed == N_TESTS:
        print("G0.36: CLOSED ({}/{})".format(passed, N_TESTS))
        return 0
    else:
        print("G0.36: FAILED ({}/{})".format(passed, N_TESTS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
