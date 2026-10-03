============================================================
HANDOVER — Governance Kernel
Session 2026-09-23 → Next Session
============================================================

## Who I am
Ahmed Ait Zaouit. GitHub: mohamedaitzaouit84-hue
ORCID: 0009-0007-3278-5577. Morocco. Termux. Zero budget.

## The project
Governance Kernel — a deterministic governance kernel for AI agents.
Repo: https://github.com/mohamedaitzaouit84-hue/governance-kernel
License: AGPL v3 + dual. Docs: CC BY-SA 4.0.

## Read first
1. docs/HANDOVER.md (this file)
2. docs/OPENING.md (integrity protocol)
3. docs/GATES_v0.7_report.md
4. docs/JOURNEY.md (log of every finding)
5. docs/PATTERNS.md
6. AUTHORS.md (AI collaboration documented)
7. docs/PRIOR_ART.md

## Status
Last commit: 2ca011a (docs: close J-0.8.11)
Last tag:    v0.7.9 (v0.7.10–v0.7.13 committed but not tagged)

V0.4: 54/54 attacks blocked, PRI = 1.0000
  verified on CI (run 35849426756)

V0.5: 5/5 gates CLOSED
  Termux: verified (explicit output today)
  CI:     verified (workflow includes V0.5; success implied)
  Colab:  verified pre-v0.7.12

V0.6: 5/5 gates CLOSED
  implied by V0.7 success (V0.7 depends on V0.6)
  explicit G0.18, G0.19 visible in CI run 35849426756

V0.7: 19/19 gates CLOSED
  verified on Termux + CI (run 35849426756, commit d2fc322)
  Colab verified on v0.7.9 (pre-v0.7.12)

For live counts, run:
  git rev-list --count HEAD
  git tag | wc -l
  gh release list
  grep -c "^## J-" docs/JOURNEY.md

## Architecture (top level)
- kernel/         — core governance loop (protected)
- authorization/  — policy, subject registry (protected)
- policy/         — policy store, YAML parsing (protected)
- control/        — kill switch, resource governor (protected)
- audit/          — append-only audit log (protected)
- seed/           — root identity, keys (protected)
- memory/         — branch memory (protected)
- agents/         — V0.5 single agents (specific files protected)
- agents/multi/   — V0.6 multi-agent (specific files protected;
                    consensus.py is the sole exception since v0.6.1)
- tests/          — gate suites V0.4 → V0.7
- docs/           — FREEZE, JOURNEY, GATES, PATTERNS, HANDOVER
- tools/          — auxiliary scripts
- bootstrap.py    — one-command fresh-clone setup

Protected paths are enforced by G0.ZZ. Do not modify.

## Session start protocol (first 5 minutes)
1. Read this file (docs/HANDOVER.md)
2. Run: python bootstrap.py
3. Run: python tests/gate_v05/run_all.py
4. Run: python tests/gate_v07/run_all.py
5. Confirm: 5/5 + 19/19
6. Only then proceed to any decision

If 5/5 or 19/19 fails, stop. Log a new finding (J-0.8.x) BEFORE any fix.

## Fresh Start Protocol

**Use when**: any of the following is true —
  - you cloned the repository for the first time
  - you rotated keys (owner_key.priv regenerated)
  - V0.5 or V0.7 fails unexpectedly after passing once
  - you ran `git checkout` or `git reset` that touched
    identity/ or branches/

**Why**: several local state files are intentionally
gitignored but must be consistent with the current owner
key. If they diverge (e.g. after a key change), the tests
fail with signature-verification errors that look like
kernel bugs but are state bugs. See J-0.8.43 / J-0.8.44 /
J-0.8.46.

**Protocol**:

    cd governance-kernel

    # 1. Remove local state that must match the current key
    rm -f identity/owner_key.priv
    rm -f identity/owner_key.pub
    rm -f identity/root_state.json
    rm -f branches/registry.jsonl
    rm -f control/kill.flag

    # 2. Bootstrap generates consistent state
    python bootstrap.py

    # 3. Run tests
    python tests/gate_v05/run_all.py
    python tests/gate_v07/run_all.py

**Expected**: 5/5 + 19/19.

**Note**: as of v0.7.18, bootstrap.py is idempotent and
detects pub/priv divergence, so step 1 is a safety
belt — bootstrap alone is usually sufficient. The explicit
removal is kept here because it is the minimal reliable
diagnosis when something is unclear.

**Verification** (optional):

    python3 - <<'EOF'
    from cryptography.hazmat.primitives import serialization
    priv = serialization.load_pem_private_key(
        open('identity/owner_key.priv','rb').read(), password=None)
    pub = serialization.load_pem_public_key(
        open('identity/owner_key.pub','rb').read())
    a = priv.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo)
    b = pub.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo)
    print('MATCH' if a == b else 'MISMATCH')
    EOF

  Must print MATCH. If MISMATCH, re-run `python bootstrap.py`
  (it will re-derive owner_key.pub from owner_key.priv).

## Golden rules
1. Freeze before code
2. Pre-registered thresholds
3. Failures logged before fixes (JOURNEY.md)
4. Kernel Untouched (unless deviation declared in FREEZE Section 0)
5. Minimal-dependency (currently 2: cryptography + pyyaml)
6. No post-hoc adjustment
7. Every number sourced
8. Honesty about limits (Threats to Validity in every report)

## Termux rules
- Small blocks (< 100 lines)
- Heredoc with quotes: `cat > file << 'EOF'`
- Verify: wc -l, tail -5
- Safe patch: count == 1 before replace
- Read before modify
- No backticks
- No /tmp — use $HOME

## Testing rule
- patch → test → commit → push → test on Colab
- local patch ≠ committed patch ≠ pushed patch
- Always test on 3 environments (Termux + GitHub Actions + Colab)

## Lessons from 2026-09-23
Ten J-0.8.x findings were addressed or documented in one session
(numbered 1, 3-11; J-0.8.2 is absent — see J-0.8.15):
- J-0.8.1: V0.5 agents fail on fresh clone
- J-0.8.2: MISSING from JOURNEY sequence
- J-0.8.3: seed/root.py assumes Path.home()
- J-0.8.4: policy_store.py also uses Path.home()
- J-0.8.5: full audit — 7 files use Path.home()
- J-0.8.6: policy signature invalid after bootstrap
- J-0.8.7: empty audit.jsonl breaks append
- J-0.8.8: "zero-dependency" claim inaccurate
- J-0.8.9: PyYAML is a second dependency
- J-0.8.10: branches/registry.jsonl not bootstrapped
           → fixed in v0.7.12
- J-0.8.11: CI shallow clone hides v0.6-closed tag
           → fixed in v0.7.13

Confirmed pattern: every fix reveals a deeper problem.
Lesson: testing 3 environments revealed what 2 hid.

## Hypotheses (see docs/PATTERNS.md)
PATTERNS.md holds 18 architectural patterns:
- P-L1 → P-L5    (5 patterns)
- P-Q1 → P-Q13   (13 patterns)

Classification and evidence live in PATTERNS.md itself.

## Eight new findings (pending — not yet in JOURNEY)
These MUST be recorded in JOURNEY.md before any fix (rule 3):

1. **J-0.8.12** — README "Six gates closed" — source not traceable.
   Reality (visible): 29 gates across V0.5–V0.7.
   Class: Documentation staleness.

2. **J-0.8.13** — Dependency count contradiction.
   - old HANDOVER: "1 dependency"
   - README: "Two external dependencies"
   - workflow: "the two external dependencies"
   Class: Contradiction.

3. **J-0.8.14** — consensus/journal.jsonl (~23 MB) untracked,
   not in .gitignore.
   Risk: `git add .` would push 23 MB to GitHub.
   Class: Hygiene + Performance + Security.

4. **J-0.8.15** — J-0.8.2 absent from JOURNEY sequence.
   No trace in file; no trace in `git log -S`.
   Class: Documentation gap.

5. **J-0.8.16** — GATES.md application table stops at V0.3.
   Does not mention V0.4 → V0.7.
   Class: Documentation staleness.

6. **J-0.8.17** — HANDOVER code-line count (5,500) understates
   reality (9,218 by `wc -l` on all .py files).
   Class: Documentation inaccuracy.

7. **J-0.8.18** — HANDOVER findings count ("14") vs JOURNEY
   `## J-` headings (18).
   Class: Documentation inaccuracy.

8. **J-0.8.19** — HANDOVER claims "7 pending DOIs".
   Only 3 unique DOIs visible anywhere in the repo.
   Class: Unverified claim.

## Open risks
- Colab not re-verified after v0.7.10–v0.7.13
- consensus/journal.jsonl untracked (J-0.8.14)
- v0.7.6 / v0.7.7 / v0.7.8 FREEZE exist without tags
- v0.7.5 has neither FREEZE nor tag
- "Six gates" original source not traceable (J-0.8.12)
- 7 pending DOIs claimed, not verifiable (J-0.8.19)

## Long-term horizon
- V0.8: external red team, SDK, real LLM integration
- arXiv preprint (candidate)

Integrity constraints (from OPENING.md):
- Never inflate claims
- Never hide failures

## Not yet verified
- Termux does NOT run V0.4 in bootstrap (confirmed by grep on 2026-09-23)
- "Six gates" original source: not traceable by git diff
- v0.7.5 has no FREEZE; v0.7.6/7/8 FREEZE exist without tags

## Tooling
- Termux (primary)
- gh CLI, git
- Python 3.13
- Google Colab (secondary test env)
- GitHub Actions (CI: Python 3.11 / 3.12 / 3.13)
- Zenodo (DOIs)
- ORCID 0009-0007-3278-5577

## Next decision (undecided)
- A: arXiv preprint
- B: V0.8 (external red team, SDK, LLM)
- C: LinkedIn publication
- D: Fix the 8 new findings (J-0.8.12 → J-0.8.19)
- E: Full stop

## Integrity rules
- No cosmetic polish. No emotion.
- Every number sourced.
- Every failure logged.
- Limits acknowledged in every report.
- Never claim "zero-dependency" — say "two dependencies".
- Never claim "Six gates" — say "29 gates (V0.5–V0.7)".

## Operational note
HANDOVER carries no variable numbers (commits, lines, findings,
releases). To query live:
  git rev-list --count HEAD
  git tag | wc -l
  grep -c "^## J-" docs/JOURNEY.md
  gh release list

Suggested order for the next session:
1. Write JOURNEY entries for the 8 pending findings
   (J-0.8.12 → J-0.8.19)
2. Fix J-0.8.14 (23 MB risk) — after recording it
3. Update README and HANDOVER
   (J-0.8.12 / J-0.8.13 / J-0.8.17 / J-0.8.18)
4. Decide on tags v0.7.10 → v0.7.13

============================================================
END OF HANDOVER — 2026-09-23
============================================================

============================================================
SESSION UPDATE — 2026-10-03
============================================================

The section above (2026-09-23) is historical. This section
supersedes it.

HEAD: 3fd19c0
Branch: main == origin/main

Gates:
  V0.4: 54/54, PRI = 1.0000
  V0.5: 5/5 CLOSED
  V0.6: 5/5 CLOSED
  V0.7: 21/21 CLOSED  (G0.42 + G0.44 added since 2026-09-23)

Sprints completed since 2026-09-23:
  Sprint 1   (J-0.8.50) FIXED 2026-10-02  commits 4dc3bdf, 7c4d448, f922c15
  Sprint 6.1 (J-0.8.60) FIXED 2026-10-03  commit 3fd19c0

Findings:
  CLOSED: 34+
  OPEN:   10 (5 CRITICAL + 5 PARTIAL)
    CRITICAL: J-0.8.51, J-0.8.52, J-0.8.53, J-0.8.57, J-0.8.58
    PARTIAL:  J-0.8.54, J-0.8.55, J-0.8.56, J-0.8.59, J-0.8.61

  (J-0.8.60 now closed — see commit 3fd19c0.)

New env vars (test isolation):
  GK_LOG_PATH   -> audit log path (default: logs/audit.jsonl)
  GK_CKPT_PATH  -> checkpoints path (default: logs/checkpoints.jsonl)

  Unset -> default production paths (behavior unchanged).
  tests/gate_v07/run_all.py sets both to a tempfile sandbox
  at startup; subprocesses inherit them. Consequence: the
  real logs/audit.jsonl is no longer touched by the suite.

Errors recorded (#21-24, in addition to #1-20):
  21. JOURNEY entry before `grep -c` -> duplication
  22. `git diff` opens pager in Termux -> `git config --global core.pager cat`
  23. Long triple-quoted heredoc patches may truncate -> use string concatenation
  24. Skipping `git add` before `git commit` -> always run `git status --short` first
  25. Adding a table row that already exists -> `grep -c <row>` before patching a table
  26. Widening sandbox without widening bootstrap -> every new env var
      requires bootstrap.py to honor it too. Otherwise bootstrap writes
      to real paths while tests read from an empty sandbox. Lesson:
      patch bootstrap BEFORE pointing run_all at the new env vars.
  27. Patching a protected file without updating G0.ZZ -> before patching
      any file under kernel/, authorization/, policy/, control/, audit/,
      seed/, or memory/, check tests/gate_v07/test_g0ZZ_kernel_untouched.py
      ALLOWED_EXCEPTIONS. If the file is not listed, add it in the same
      commit. G0.ZZ compares `git diff v0.6-closed HEAD`, so it fails on
      committed changes even when the code works.

Next session (Sprint 6 Phase 2):
  - kernel/context.py (contextvar-based sandbox())
  - env-var pattern extended to identity/, control/, branches/, memory/
  - J-0.8.61 (Fresh Start Protocol — soft/hard modes)
  - gate G0.45 (deeper subprocess isolation)

Then:
  Sprint 2: J-0.8.52 (kill switch signed state), J-0.8.55 (subjects signed)
  Sprint 3: J-0.8.54 (bootstrap consent), J-0.8.57 (governor auth)
  Sprint 4: J-0.8.53 (key encryption), J-0.8.51 (external anchor)
  Sprint 5: J-0.8.58 (manifest signed)
  Sprint 6.2: J-0.8.59 (checkpoint key rotation)

============================================================
END OF SESSION UPDATE — 2026-10-03
============================================================
