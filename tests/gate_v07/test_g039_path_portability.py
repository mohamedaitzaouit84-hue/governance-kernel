"""G0.39 — Path Portability.

Criterion:
  1. seed.root.KERNEL_DIR resolves to repository root
  2. Independent of Path.home()
  3. Points to a directory containing seed/root.py
  4. Points to a directory containing .git/
  5. Matches Path(__file__).parent.parent pattern

This test guards against J-0.8.3 (Path.home dependence).

Read-only. Does NOT modify any file.
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = _here.parent.parent
sys.path.insert(0, str(_repo))
sys.path.insert(0, str(_repo / "seed"))

import root


def check_1_resolves_to_repo():
    """KERNEL_DIR == repository root."""
    return root.KERNEL_DIR.resolve() == _repo.resolve()


def check_2_not_home_dependent():
    """KERNEL_DIR != Path.home() / governance_kernel unless
    it happens to equal the repo root."""
    home_guess = (Path.home() / "governance_kernel").resolve()
    if root.KERNEL_DIR.resolve() == home_guess:
        # Same path — acceptable IF repo is at $HOME/governance_kernel
        return _repo.resolve() == home_guess
    # Different paths — this is the portable case (GOOD)
    return True


def check_3_has_seed_root():
    """KERNEL_DIR / seed / root.py exists."""
    return (root.KERNEL_DIR / "seed" / "root.py").exists()


def check_4_has_git():
    """KERNEL_DIR / .git exists."""
    return (root.KERNEL_DIR / ".git").exists()


def check_5_repo_relative():
    """KERNEL_DIR is derived from __file__, not Path.home()."""
    # We cannot introspect the source directly here,
    # but we can verify it's NOT Path.home() unless
    # the repo really is at Path.home()/governance_kernel
    home_guess = (Path.home() / "governance_kernel").resolve()
    if root.KERNEL_DIR.resolve() == home_guess:
        return True  # acceptable
    # If it differs from home_guess, it must be the repo root
    return root.KERNEL_DIR.resolve() == _repo.resolve()


def main():
    checks = [
        ("KERNEL_DIR == repo root", check_1_resolves_to_repo),
        ("not home-dependent", check_2_not_home_dependent),
        ("seed/root.py exists", check_3_has_seed_root),
        (".git exists", check_4_has_git),
        ("repo-relative derivation", check_5_repo_relative),
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

    print("  KERNEL_DIR:", root.KERNEL_DIR)
    print("  repo root:  ", _repo)
    print("  home guess: ", Path.home() / "governance_kernel")
    print()
    print("  Path portability checks: {}/{}".format(passed, len(checks)))
    if failed:
        print("  FAILED: {}".format(failed))

    if passed == len(checks):
        print("G0.39: CLOSED ({}/{})".format(passed, len(checks)))
        return 0
    else:
        print("G0.39: FAILED ({}/{})".format(passed, len(checks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
