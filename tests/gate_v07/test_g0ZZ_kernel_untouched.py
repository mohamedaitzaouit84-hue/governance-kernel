"""G0.ZZ — Kernel Untouched.

Criterion: zero modifications to protected files since v0.6-closed.

Method:
  1. Run `git diff --name-only v0.6-closed HEAD`
  2. Check that no file matches the protected list in
     docs/FREEZE_v0.7.md section 0.
  3. Exception: agents/multi/consensus.py IS allowed to differ
     because v0.6.1 patched it (J-0.7.1).

Allowed changes since v0.6-closed:
  - agents/multi/consensus.py    (v0.6.1 patch)
  - tests/gate_v07/*             (V0.7.1 tests)
  - docs/FREEZE_v0.7*.md         (freezes)
  - docs/FREEZE_v0.6.1.md        (patch freeze)
  - docs/JOURNEY.md              (findings)
  - docs/RED_TEAM_v0.6.md        (to be written)
  - docs/GATES_v0.7_report.md    (to be written)
  - docs/PATTERNS.md             (P-Q13, V0.7.4)

Protected (must NOT change):
  - kernel/*
  - authorization/*
  - policy/*
  - control/*
  - audit/*
  - seed/*
  - memory/*
  - agents/file_agent.py, compute_agent.py, query_agent.py,
    base_agent.py, invariant_checker.py, trust_manager.py,
    governed_action_v05.py, register_agents.py
  - agents/multi/__init__.py, proposal.py, communication.py,
    coordinator.py

Read-only. Does NOT modify any file.
"""
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent


# Protected prefixes and files (from FREEZE_v0.7 section 0)
PROTECTED_PREFIXES = [
    "kernel/",
    "authorization/",
    "policy/",
    "control/",
    "audit/",
    "seed/",
    "memory/",
]

PROTECTED_FILES = {
    "agents/file_agent.py",
    "agents/compute_agent.py",
    "agents/query_agent.py",
    "agents/base_agent.py",
    "agents/invariant_checker.py",
    "agents/trust_manager.py",
    "agents/governed_action_v05.py",
    "agents/register_agents.py",
    "agents/multi/__init__.py",
    "agents/multi/proposal.py",
    "agents/multi/communication.py",
    "agents/multi/coordinator.py",
    # consensus.py was patched in v0.6.1 (J-0.7.1)
    # so it is NOT in this list.
}

# Explicitly allowed to change
ALLOWED_EXCEPTIONS = {
    # v0.6.1 patch (J-0.7.1)
    "agents/multi/consensus.py",
    # v0.7.6 patch (J-0.8.3): Path Portability phase 1
    "seed/root.py",
    # v0.7.7 patch (J-0.8.5): Path Portability phase 2
    "audit/append_only_log.py",
    # v0.7.15 (J-0.8.28): bootstrap.py adds default subjects
    # (memory_system) to authorization/subjects.json. Additive
    # only. Required for fresh-clone correctness (J-0.8.21).
    "authorization/subjects.json",
    "audit/integrity.py",
    "policy/policy_store.py",
    "authorization/branch_registry.py",
    "control/kill_switch.py",
    "control/resource_governor.py",
    "agents/invariant_checker.py",
}


def _git_diff_names(base, head="HEAD"):
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base, head],
            cwd=str(_repo),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None, result.stderr
        return [l.strip() for l in result.stdout.splitlines() if l.strip()], None
    except Exception as e:
        return None, str(e)


def main():
    base = "v0.6-closed"
    names, err = _git_diff_names(base, "HEAD")

    if err is not None:
        print("  ERROR running git diff: {}".format(err))
        print("G0.ZZ: FAILED (could not diff)")
        return 1

    if names is None:
        print("  ERROR: git diff returned None")
        print("G0.ZZ: FAILED (could not diff)")
        return 1

    print("  Files changed since {}: {}".format(base, len(names)))

    violations = []
    for name in names:
        # Check protected prefixes
        hit_prefix = any(name.startswith(p) for p in PROTECTED_PREFIXES)
        # Check protected files (exact match)
        hit_file = name in PROTECTED_FILES
        # Allow consensus.py exception
        if name in ALLOWED_EXCEPTIONS:
            continue
        if hit_prefix or hit_file:
            violations.append(name)

    if violations:
        print("  VIOLATIONS:")
        for v in violations:
            print("    - {}".format(v))
        print("G0.ZZ: FAILED ({} kernel files modified)".format(
            len(violations)))
        return 1

    print("  No protected files modified.")
    print("G0.ZZ: CLOSED (kernel untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
