#!/usr/bin/env python3
"""bootstrap.py — Prepare a fresh clone for full operation.

Run this ONCE after git clone to:
  1. Generate a fresh owner key (if missing)
  2. Create an empty audit log (if missing)
  3. Register owner + agents into subjects.json
  4. Initialize root_state.json
  5. Print the new owner fingerprint

This is required because .gitignore excludes:
  - identity/owner_key.priv    (safety)
  - identity/root_state.json   (safety)
  - logs/audit.jsonl           (local log)

See docs/JOURNEY.md J-0.8.1 for context.
"""

import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "seed"))
sys.path.insert(0, str(REPO / "audit"))
sys.path.insert(0, str(REPO / "authorization"))

import root
import append_only_log as audit


DEFAULT_SUBJECTS = {
    "owner":            {"role": "owner",            "trust": 1.0},
    "system":           {"role": "system",           "trust": 0.9},
    "memory_system":    {"role": "system",           "trust": 0.9},
    "agent_high_1":     {"role": "agent_high",       "trust": 0.8},
    "agent_mid_1":      {"role": "agent_mid",        "trust": 0.6},
    "agent_low_1":      {"role": "agent_low",        "trust": 0.3},
    "file_agent_1":     {"role": "file_agent",       "trust": 0.1},
    "compute_agent_1":  {"role": "compute_agent",    "trust": 0.1},
    "query_agent_1":    {"role": "query_agent",      "trust": 0.1},
}


def step_owner_key():
    """Generate owner key if missing. Return fingerprint."""
    priv = REPO / "identity" / "owner_key.priv"
    if priv.exists():
        print("  [SKIP] owner_key.priv already exists")
    else:
        print("  [GEN ] owner_key.priv missing — generating")
        root.generate_owner_key()
    return root.fingerprint()


def step_root_state():
    """Record root state if missing."""
    state = REPO / "identity" / "root_state.json"
    if state.exists():
        print("  [SKIP] root_state.json already exists")
    else:
        print("  [GEN ] root_state.json missing — recording")
        root.record_root_state()


def step_audit_log():
    """Create empty audit log if missing."""
    log = REPO / "logs" / "audit.jsonl"
    if log.exists():
        print("  [SKIP] audit.jsonl already exists")
    else:
        print("  [GEN ] audit.jsonl missing — creating empty")
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("", encoding="utf-8")


def step_subjects():
    """Ensure subjects.json has all default subjects."""
    path = REPO / "authorization" / "subjects.json"
    if not path.exists():
        print("  [GEN ] subjects.json missing — creating")
        data = {"version": "0.4.1", "subjects": {}}
    else:
        data = json.loads(path.read_text(encoding="utf-8"))

    subjects = data.setdefault("subjects", {})
    added = []
    for key, val in DEFAULT_SUBJECTS.items():
        if key not in subjects:
            subjects[key] = val
            added.append(key)

    if added:
        print("  [ADD ] subjects added: " + ", ".join(added))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:
        print("  [SKIP] all subjects already registered")


def step_register_branches():
    """Register the three default V0.5 agents as branches.

    Fresh clones have no branches/registry.jsonl (it is in
    .gitignore). This step reuses agents/register_agents.py
    to register FileAgent, ComputeAgent, QueryAgent with the
    owner's signature.

    Idempotent: already-registered branches are skipped.
    """
    import subprocess
    script = REPO / "agents" / "register_agents.py"
    if not script.exists():
        print("  [SKIP] agents/register_agents.py not found")
        return

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode == 0:
        # Count "REGISTERED" vs "SKIPPED"
        registered = result.stdout.count("REGISTERED")
        skipped = result.stdout.count("SKIPPED")
        print("  [OK  ] branches: {} registered, {} skipped".format(
            registered, skipped))
    else:
        print("  [WARN] register_agents.py exited {}".format(
            result.returncode))
        # Show last lines for debugging
        for line in (result.stdout + result.stderr).splitlines()[-3:]:
            print("         " + line)


def step_register_memory_branch():
    """Register the 'memory' storage branch.

    Fresh clones have no branches/registry.jsonl (it is in
    .gitignore). memory/gate.py needs a registered 'memory'
    branch to authorize memory operations. This step reuses
    memory/register_branch.py with the owner's signature.

    Idempotent: if 'memory' is already registered, skipped.
    """
    import subprocess
    script = REPO / "memory" / "register_branch.py"
    if not script.exists():
        print("  [SKIP] memory/register_branch.py not found")
        return

    # Check whether 'memory' is already registered
    try:
        if str(REPO / "authorization") not in sys.path:
            sys.path.insert(0, str(REPO / "authorization"))
        import branch_registry as br
        branches = br.list_branches()
        if any(b.get("name") == "memory" for b in branches):
            print("  [SKIP] memory branch already registered")
            return
    except Exception as exc:
        print("  [WARN] could not check registry: {}".format(exc))

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode == 0:
        print("  [OK  ] memory branch registered")
    else:
        print("  [WARN] memory/register_branch.py exited {}".format(
            result.returncode))
        for line in (result.stdout + result.stderr).splitlines()[-3:]:
            print("         " + line)


def step_policy_signature():
    """Re-sign default.yaml if signature is invalid.

    Fresh clones have default.yaml + default.yaml.sig from Git.
    The signature was made with the ORIGINAL owner key.
    bootstrap.py generates a NEW key.
    We must re-sign so policy_store.load() succeeds.
    """
    import hashlib
    policy_dir = REPO / "policy" / "policies"
    policy_file = policy_dir / "default.yaml"
    sig_file = policy_dir / "default.yaml.sig"

    if not policy_file.exists():
        print("  [SKIP] default.yaml not found")
        return
    if not sig_file.exists():
        print("  [SKIP] default.yaml.sig not found")
        return

    text = policy_file.read_text(encoding="utf-8")
    policy_hash = hashlib.sha256(text.encode("utf-8")).hexdigest().encode("utf-8")

    try:
        sig = bytes.fromhex(sig_file.read_text(encoding="utf-8").strip())
        if root.verify(policy_hash, sig):
            print("  [SKIP] default.yaml.sig valid")
            return
    except Exception:
        pass  # invalid hex or verify error -> resign below

    print("  [FIX ] policy signature invalid — re-signing")
    new_sig = root.sign(policy_hash)
    sig_file.write_text(new_sig.hex(), encoding="utf-8")
    print("  [FIX ] default.yaml.sig regenerated")


def main():
    print("=" * 60)
    print("Governance Kernel — bootstrap.py")
    print("=" * 60)
    print()
    print("Preparing fresh clone...")
    print()

    step_owner_key()
    step_root_state()
    step_audit_log()
    step_subjects()
    step_register_branches()
    step_register_memory_branch()
    step_policy_signature()

    print()
    print("=" * 60)
    print("Fingerprint:", root.fingerprint())
    print("=" * 60)
    print()
    print("Bootstrap complete. You may now run:")
    print("  python tests/gate_v07/run_all.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
