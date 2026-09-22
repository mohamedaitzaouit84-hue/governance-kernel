"""G0.37 — Delegation Revoked (H24 part 3).

Criterion: 5/5 revoked delegations are denied.

This is the core test of H24: revocation mid-flight.

For each:
  - Create delegation with long TTL (won't expire during test)
  - Verify it works (before revocation)
  - Revoke it
  - Verify it is denied immediately
  - Verify it is still denied after further attempts

Read-only. Does NOT modify V0.5 or V0.6 files.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))

from agents.multi.delegation import (
    Delegation, DelegationRegistry, DelegationError,
)

N_TESTS = 5
LONG_TTL = 3600  # 1 hour


def _test_one(i):
    """Return (bool, msg). True if revocation is enforced."""
    reg = DelegationRegistry()

    action = "file_read" if i % 2 == 0 else "compute_add"
    grantee = "file_agent_1" if i % 2 == 0 else "compute_agent_1"

    d = Delegation(
        granter_id="owner",
        grantee_id=grantee,
        scope=[action],
        ttl_seconds=LONG_TTL,
    )
    reg.register(d)

    # 1. Before revocation: allowed
    ok, _ = reg.is_allowed(grantee, action)
    if not ok:
        return False, "not allowed before revocation"

    # 2. Not revoked initially
    if d.is_revoked():
        return False, "wrongly revoked initially"

    # 3. Revoke
    reg.revoke(d.delegation_id)

    # 4. Revoked
    if not d.is_revoked():
        return False, "not marked revoked after revoke()"

    # 5. After revocation: denied
    ok, reason = reg.is_allowed(grantee, action)
    if ok:
        return False, "allowed after revocation"

    # 6. Not expired (still within TTL)
    if d.is_expired():
        return False, "wrongly expired"

    # 7. is_valid returns False (because revoked)
    if d.is_valid():
        return False, "is_valid True after revoke"

    # 8. Double revoke raises
    try:
        reg.revoke(d.delegation_id)
        return False, "double revoke accepted"
    except DelegationError:
        pass  # expected

    # 9. Revocation is permanent
    ok, _ = reg.is_allowed(grantee, action)
    if ok:
        return False, "allowed after second attempt"

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

    print("  Revoked delegations denied: {}/{}".format(passed, N_TESTS))
    if failed:
        for i, m in failed[:5]:
            print("    test {}: {}".format(i, m))

    if passed == N_TESTS:
        print("G0.37: CLOSED ({}/{})".format(passed, N_TESTS))
        return 0
    else:
        print("G0.37: FAILED ({}/{})".format(passed, N_TESTS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
