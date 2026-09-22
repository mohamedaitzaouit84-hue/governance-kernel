"""G0.34 — V0.5 agents untouched (H23 part 4).

Criterion: zero modifications to V0.5 agent files since v0.6-closed.

Method:
  1. Run `git diff --name-only v0.6-closed HEAD`
  2. Check that no file matches the V0.5 agent list.
  3. V0.5 files MUST be byte-identical to v0.6-closed state.

Allowed changes since v0.6-closed:
  - agents/multi/consensus.py    (v0.6.1 patch)
  - agents/multi/coordinator_v2.py (V0.7.3 new)
  - tests/gate_v07/*             (V0.7.1, V0.7.2, V0.7.3 tests)
  - docs/*                       (freezes, reports)
  - agents/multi/benchmark/*     (V0.7.2)

V0.5 agent files (MUST NOT change):
  - agents/file_agent.py
  - agents/compute_agent.py
  - agents/query_agent.py
  - agents/base_agent.py
  - agents/invariant_checker.py
  - agents/trust_manager.py
  - agents/governed_action_v05.py
  - agents/register_agents.py
  - agents/__init__.py

Read-only. Does NOT modify any file.
"""
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent


# V0.5 agent files that MUST NOT change
V05_FILES = {
    "agents/file_agent.py",
    "agents/compute_agent.py",
    "agents/query_agent.py",
    "agents/base_agent.py",
    "agents/invariant_checker.py",
    "agents/trust_manager.py",
    "agents/governed_action_v05.py",
    "agents/register_agents.py",
    "agents/__init__.py",
}


# Files in V05_FILES that may change, with documented justification.
# Preserves the SPIRIT of G0.34 (detect UNDOCUMENTED modifications)
# while acknowledging DOCUMENTED ones.
ALLOWED_EXCEPTIONS = {
    # V0.7.7 Path Portability (J-0.8.5)
    # Reference: docs/FREEZE_v0.7.7.md section 0
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
        print("G0.34: FAILED (could not diff)")
        return 1

    if names is None:
        print("  ERROR: git diff returned None")
        print("G0.34: FAILED (could not diff)")
        return 1

    print("  Files changed since {}: {}".format(base, len(names)))

    violations = []
    for name in names:
        if name in V05_FILES:
            if name in ALLOWED_EXCEPTIONS:
                continue  # documented exception
            violations.append(name)

    if violations:
        print("  VIOLATIONS:")
        for v in violations:
            print("    - {}".format(v))
        print("G0.34: FAILED ({} V0.5 files modified)".format(len(violations)))
        return 1

    print("  No V0.5 agent files modified.")
    print("G0.34: CLOSED (V0.5 untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
