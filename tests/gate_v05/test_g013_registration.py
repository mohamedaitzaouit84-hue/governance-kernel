"""G0.13 — Agent Registration.

Criterion: 3/3 agents registered with owner signature.
Verifies: branch exists + signature valid + permissions match spec.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo / "authorization"))
sys.path.insert(0, str(_repo / "seed"))

import branch_registry
import root

EXPECTED = {
    "file_agent_1":    ["file_read", "file_list", "file_write", "file_delete"],
    "compute_agent_1": ["compute_add", "compute_sub", "compute_mul", "compute_div"],
    "query_agent_1":   ["query_lookup", "query_count", "query_verify"],
}


def main():
    branches = branch_registry.list_branches()
    by_name = {b["name"]: b for b in branches}
    passed = 0
    total = 0

    for name, expected_perms in EXPECTED.items():
        total += 1
        b = by_name.get(name)
        if b is None:
            print("  FAIL: {} not registered".format(name))
            continue

        # permissions match (as sets)
        actual = sorted(b["requested_permissions"])
        if sorted(expected_perms) != actual:
            print("  FAIL: {} perms mismatch: {} vs {}".format(name, actual, sorted(expected_perms)))
            continue

        # signature valid
        commitment = branch_registry.commitment(
            b["name"], b["kind"], b["requested_permissions"]
        )
        sig = bytes.fromhex(b["owner_signature"])
        if not root.verify(commitment, sig):
            print("  FAIL: {} signature invalid".format(name))
            continue

        print("  PASS: {} (branch_id={})".format(name, b["branch_id"]))
        passed += 1

    print("G0.13: {}/{} registered and verified".format(passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
