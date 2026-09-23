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
