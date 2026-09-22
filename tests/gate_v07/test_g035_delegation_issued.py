"""G0.35 — Delegation Issued (H24 part 1).

Criterion: 5/5 delegations issued correctly.

For each:
  - Create delegation
  - Register it
  - Verify it appears in registry
  - Verify lookup works
  - Verify scope is respected

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


def _test_one(i):
    """Return True if delegation issued correctly."""
    reg = DelegationRegistry()

    scope = ["file_read", "file_list"] if i % 2 == 0 else ["compute_add"]
    grantee = "file_agent_1" if i % 2 == 0 else "compute_agent_1"

    d = Delegation(
        granter_id="owner",
        grantee_id=grantee,
        scope=scope,
        ttl_seconds=300 + i,
    )

    # 1. Not yet registered
    if reg.lookup(d.delegation_id) is not None:
        return False

    # 2. Register
    did = reg.register(d)
    if did != d.delegation_id:
        return False

    # 3. Lookup works
    found = reg.lookup(d.delegation_id)
    if found is not d:
        return False

    # 4. Appears in for_grantee
    grantee_list = reg.for_grantee(grantee)
    if d not in grantee_list:
        return False

    # 5. Scope respected
    for action in scope:
        if not d.allows(action):
            return False

    # 6. Not in scope, not allowed
    if d.allows("file_write") and "file_write" not in scope:
        return False

    # 7. Valid initially
    if not d.is_valid():
        return False

    return True


def main():
    passed = 0
    failed = []
    for i in range(N_TESTS):
        try:
            if _test_one(i):
                passed += 1
            else:
                failed.append((i, "verification failed"))
        except Exception as e:
            failed.append((i, "{}: {}".format(type(e).__name__, e)))

    print("  Delegations issued correctly: {}/{}".format(passed, N_TESTS))
    if failed:
        for i, m in failed[:5]:
            print("    test {}: {}".format(i, m))

    if passed == N_TESTS:
        print("G0.35: CLOSED ({}/{})".format(passed, N_TESTS))
        return 0
    else:
        print("G0.35: FAILED ({}/{})".format(passed, N_TESTS))
        return 1


if __name__ == "__main__":
    sys.exit(main())
