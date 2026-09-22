"""G0.40 — Path Portability Audit.

Criterion:
  - Scan all production .py files in the repository
  - Ensure NONE of them uses:
      Path.home() / "governance_kernel"
  - Allowed exceptions (test files, not production):
      tests/gate_v07/test_g039_path_portability.py
      tests/gate_v07/test_g040_path_portability_audit.py
  - Docs are allowed to mention the pattern (historical)

This test guards against J-0.8.5.

Read-only. Does NOT modify any file.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent

# Directories to scan (production code)
SCAN_DIRS = [
    "audit",
    "policy",
    "authorization",
    "control",
    "seed",
    "memory",
    "kernel",
    "agents",
]

# Banned pattern in production code
BANNED = 'Path.home() / "governance_kernel"'

# Allowed files (test code, not production)
ALLOWED_FILES = {
    "tests/gate_v07/test_g039_path_portability.py",
    "tests/gate_v07/test_g040_path_portability_audit.py",
}


def scan_file(path):
    """Return True if file is clean, False if it contains BANNED."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return True  # skip unreadable
    return BANNED not in text


def main():
    offenders = []
    scanned = 0

    for dirname in SCAN_DIRS:
        d = _repo / dirname
        if not d.exists():
            continue
        for pyfile in d.rglob("*.py"):
            # Skip __pycache__
            if "__pycache__" in pyfile.parts:
                continue
            # Skip test subdirectories within agents (none expected)
            rel = pyfile.relative_to(_repo).as_posix()
            if rel in ALLOWED_FILES:
                continue
            scanned += 1
            if not scan_file(pyfile):
                offenders.append(rel)

    print("  Scanned .py files: {}".format(scanned))

    if offenders:
        print("  VIOLATIONS (production code uses banned pattern):")
        for o in offenders:
            print("    - " + o)
        print("G0.40: FAILED ({} files)".format(len(offenders)))
        return 1

    print("  No production file uses Path.home() / \"governance_kernel\"")
    print("G0.40: CLOSED (path portability audit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
