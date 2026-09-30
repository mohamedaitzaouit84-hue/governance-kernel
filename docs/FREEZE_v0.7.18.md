# FREEZE — v0.7.18

**Type**: Bugfix release (no deviation)
**Date**: 2026-09-30
**Predecessor**: v0.7.17 (1a27404)
**Findings closed**: J-0.8.43, J-0.8.44, J-0.8.45, J-0.8.46
**Findings reviewed**: J-0.8.26 (WONTFIX)

## Section 0 — Deviation Declaration

**Protected files modified**: NONE.

All fixes in this release target files that are outside
`PROTECTED_PREFIXES` and `PROTECTED_FILES` in
tests/gate_v07/test_g0ZZ_kernel_untouched.py:

  - bootstrap.py                (not protected)
  - tests/gate_v05/run_all.py   (not protected)
  - tests/gate_v07/run_all.py   (not protected)
  - docs/HANDOVER.md            (not protected)
  - .gitignore                  (not protected)
  - identity/owner_key.pub      (removed from tracking;
                                 identity/ not protected)

Verification:
  G0.ZZ: CLOSED (kernel untouched) on all commits in this
  release.

Therefore Section 0 is empty: no exception needs to be
added to ALLOWED_EXCEPTIONS.

## Section 1 — Scope

### J-0.8.43 — bootstrap pub/priv + .sig
Commit: d136407

  Two sub-bugs fixed in bootstrap.py:

  A. step_owner_key() now:
     - reads owner_key.priv
     - derives the corresponding public key
     - compares with owner_key.pub
     - if they differ, re-derives owner_key.pub
     Previously the function only checked for the existence
     of the private key; a diverged pub was silently left
     in place, breaking every signature verification.

  B. step_policy_signature() now:
     - if default.yaml.sig is missing, signs default.yaml
       and writes the signature
     Previously the function printed a SKIP message and
     returned, leaving the policy unsigned.

  Files: bootstrap.py (+61 / -8).
  Idempotent: safe to run repeatedly.

### J-0.8.44 — kill.flag reset
Commit: 045d469

  control/kill.flag persists on disk between test runs.
  G0.17 activates it (by design, to verify the mechanism)
  and clears it on normal completion. If a prior run
  aborted before clearing, every subsequent V0.5 run
  failed at G0.14/15/17 with:
    governed_action_v05.ActionDenied: kill switch active

  Three coordinated fixes:
  A. bootstrap.py: new step_reset_kill_switch().
  B. tests/gate_v05/run_all.py: clears kill.flag on entry.
  C. tests/gate_v07/run_all.py: clears kill.flag on entry
     (after its auto-bootstrap step).

  Result: V0.5 and V0.7 are now idempotent. Running them
  twice in the same clone produces the same 5/5 + 19/19.

  Files: bootstrap.py (+18), run_all.py v05 (+8),
  run_all.py v07 (+7).

### J-0.8.45 — Fresh Start Protocol
Commit: 2b0a474

  docs/HANDOVER.md now contains an explicit
  "Fresh Start Protocol" section. It documents:
    - when to use it (first clone, key rotation,
      unexpected failure after a passing run)
    - why it exists (gitignored local state can diverge
      from the current owner key)
    - the exact commands
    - a MATCH verification snippet

  Files: docs/HANDOVER.md (+62).

### J-0.8.46 — owner_key.pub untracked
Commit: 2b0a474

  identity/owner_key.pub was committed to git (the
  original developer's public key), while
  identity/owner_key.priv was gitignored. A fresh clone
  therefore started with a mismatched pair.

  Changes:
    - .gitignore now lists identity/owner_key.pub.
    - git rm --cached identity/owner_key.pub removes it
      from tracking (the file stays on disk where it
      exists).
  Consequence: every clone generates its own pair via
  bootstrap.py.

  Files: .gitignore (+1), identity/owner_key.pub (-3,
  untracked).

## Section 2 — Pre-registered thresholds

No new thresholds. No behavior changes to any gate
criterion. The bugfixes restore the intended behavior of
already-registered gates.

## Section 3 — Verification

### CI (GitHub Actions)
All four commits pushed in this release passed CI
(Python 3.11, 3.12, 3.13):
  - 2361b63  ✓
  - d136407  ✓
  - 045d469  ✓
  - 2b0a474  ✓

### Local (Termux)
  V0.5 = 5/5 CLOSED
  V0.7 = 19/19 CLOSED
  Idempotency verified: V0.5 → 5/5 twice in a row.

### Colab (fresh clone)
  V0.5 = 5/5 CLOSED
  V0.7 = 19/19 CLOSED
  (Verified on 61a8df0 before these fixes; re-verification
  will be performed for v0.7.18.)

## Section 4 — Non-goals

The following were explicitly NOT changed:

  - kernel/*            (untouched)
  - policy/*            (untouched)
  - authorization/*     (untouched)
  - control/*           (untouched, other than kill.flag
                         reset which is performed by the
                         caller, not by control itself)
  - audit/*             (untouched)
  - seed/*              (untouched)
  - memory/*            (untouched)
  - agents/*            (untouched)

## Section 5 — Scientific note

The four findings closed in this release share a single
theme: reproducibility depends on state, not only on code.
A repository can pass every test in CI and still fail in
a developer's clone if local, gitignored state (keys,
registries, kill flags) is not kept consistent with the
current commit.

J-0.8.43 / 44 / 46 address the state side. J-0.8.45
addresses the documentation side. Together they convert
a project that "works on the author's machine" into a
project that "works on a fresh machine, from the README,
without hand-holding."

This is a precondition for external reproducibility and
for any external audit of the project's claims.

## Section 6 — Follow-up

  - Re-verify v0.7.18 on Colab (fresh clone).
  - Publish tag v0.7.18 and a GitHub Release.
  - Continue with J-0.8.32 (SDK / packaging).
  - Prepare the JOSS software paper.

---

**Signed-off-by**: Ahmed Ait Zaouit <mohamedaitzaouit84@gmail.com>
**Date**: 2026-09-30
