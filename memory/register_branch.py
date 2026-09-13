"""تسجيل فرع الذاكرة بتوقيع المالك."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "seed"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "authorization"))
import root
import branch_registry as br
import append_only_log as audit


def main():
    name = "memory"
    kind = "storage"
    perms = [
        "memory:read",
        "memory:write",
        "memory:graph_traverse",
        "memory:trail_reinforce",
        "memory:swarm_query",
    ]

    # 1) بناء الالتزام
    msg = br.commitment(name, kind, perms)
    print(f"commitment_hash: {msg.hex()[:16]}...")

    # 2) توقيع المالك
    sig = root.sign(msg).hex()
    print(f"signature: {sig[:16]}...")

    # 3) التسجيل
    result = br.register(name, kind, perms, sig)
    if not result["ok"]:
        print(f"FAILED: {result['reason']}")
        sys.exit(1)

    print(f"OK: branch registered")
    print(f"branch_id: {result['branch_id']}")
    print(f"permissions: {result['record']['requested_permissions']}")

    # 4) التحقق
    all_branches = br.list_branches()
    print(f"\ntotal branches: {len(all_branches)}")
    for b in all_branches:
        print(f"  - {b['branch_id']} | {b['name']} | {b['kind']}")


if __name__ == "__main__":
    main()
