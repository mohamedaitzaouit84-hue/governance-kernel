# رحلة بناء V0.1 — بأخطائها وتصحيحاتها

> الغاية: توثيق كل خطأ واجهناه وكيف صُحِّح.
> من لا يوثّق أخطاءه يعيدها.

## الجلسة 1: الإعداد الأولي

### الخطأ #1: التطبيق الخطأ في F-Droid
**السياق**: البحث عن Termux أعطى قائمة إضافات.
**الخطأ**: كان يمكن اختيار إضافة بدل التطبيق الأساسي.
**التصحيح**: تحديد Termux Terminal emulator with packages.
**الدرس**: في F-Droid، ابحث عن الاسم المجرّد.

## الجلسة 2: تثبيت الأدوات

### ملاحظة: Python مُثبَّت مسبقاً
Termux الحديث يأتي مع Python 3.13.
لا حاجة لتثبيته يدوياً.

## الجلسة 3: البذرة (Genesis)
توليد مفتاح Ed25519. بصمة: 9f40df378e6a0199.
التوقيع والتحقق يعملان. كشف التعديل يعمل.
**لا أخطاء.**

## الجلسة 4: السجل (Audit Log)
121 سجلاً. تعديل seq=60 كُشف فوراً.
2 checkpoints موقّعة.
**لا أخطاء.**

## الجلسة 5: Policy Engine + Permission Gate

### الخطأ #2: مجلد policy/policies/ غير موجود
**السياق**: cat > policy/policies/default.yaml
**الخطأ**: policy/policies/ لم يكن موجوداً. Bash رفض الكتابة.
**الأثر**: default.yaml لم يُكتب. permission_gate فشل لاحقاً.
**التصحيح**: mkdir -p policy/policies ثم إعادة الكتابة.
**الدرس**: mkdir -p قبل كل كتابة ملف في مسار متداخل.
**درس إضافي**: Bash لا يُظهر تحذيراً واضحاً في بعض الحالات.

## الجلسة 6: اختبار كشف تعديل السياسة

### الخطأ #3: /tmp غير موجود في Termux
**السياق**: cp policy/policies/default.yaml /tmp/default.yaml.bak
**الخطأ**: /tmp غير موجود. النسخة الاحتياطية لم تُنشأ.
**الأثر**: بعد التعديل، لم نستطع الاسترجاع. السياسة بقيت allow.
**التصحيح**:
1. إعادة كتابة default.yaml يدوياً.
2. حذف default.yaml.sig لإجبار إعادة التوقيع.
3. من الآن، استخدام $HOME بدل /tmp.
**الدرس**: Termux ≠ Linux عادي. المسارات المؤقتة في $HOME.

## الجلسة 7: Kill Switch + Resource Governor + Branch Registry

### الخطأ #4: TEST 5 فشل بشكل متوقع
**السياق**: TEST 4 استهلك 60 استدعاء على نفس الفرع.
TEST 5 حاول استدعاءً جديداً على نفس الفرع.
**الظاهر**: ActionDenied: limit 60/min exceeded
**التشخيص**: ليس خطأً — هذا السلوك الصحيح.
**التصحيح**: عزل الاختبارات. rg.reset() قبل TEST 5.
**الدرس**: اختبارات النظام بحالة مشتركة تحتاج تنظيفاً بينها.
**درس أعمق**: هذا كشف قوة النظام. الفرع لا يتجاوز حصته.

## خلاصة الأخطاء

| # | الخطأ | النوع | الأثر | التصحيح |
|---|-------|------|-------|---------|
| 1 | اختيار إضافة Termux | بشري | لا شيء | التطبيق الصحيح |
| 2 | policies/ غير موجود | تقني | default.yaml مفقود | mkdir -p |
| 3 | /tmp غير موجود | بيئي | السياسة بقيت معدّلة | $HOME |
| 4 | TEST 5 "فشل" | اختباري | لا شيء | عزل الاختبارات |

3 أخطاء بيئية/تقنية، 1 اختباري. لا أخطاء منطقية في الكود.

## ما تعلّمناه عن Termux
1. /tmp غير موجود — استخدم $HOME.
2. Python مُثبَّت مسبقاً.
3. F-Droid — ابحث عن الاسم المجرّد.
4. mkdir -p إلزامي قبل أي كتابة ملف.
5. ls البصري ضروري بعد كل كتابة.
6. GitHub CLI متاح عبر pkg install gh.

## ما لم نختبره بعد (شفافية)
- Persistence بعد إعادة تشغيل الهاتف.
- أداء السجل مع 10K+ سجل.
- سلوك النظام عند امتلاء التخزين.
- توقيع بمفاتيح متعددة (multi-owner).
- Migration بين الأجهزة.

داخل نطاق V0.2/V0.3، ليست عيوباً في V0.1.

## الجلسة 8: الرفع على GitHub

### الخطأ #5: رمز GitHub بصلاحيات كاملة (حادثة أمنية)

السياق: عند استخدام gh auth login، الرمز الذي أُنشئ منح
صلاحيات كاملة تقريباً:
admin:enterprise, admin:gpg_key, admin:org, admin:org_hook,
admin:public_key, admin:repo_hook, admin:ssh_signing_key,
audit_log, codespace, copilot, delete_repo, delete:packages,
gist, notifications, project, repo, user, workflow,
write:discussion, write:network_configurations, write:packages.

هذا ينتهك مبدأ Least Privilege الذي نصّ عليه الميثاق.

الأثر: أي شخص يحصل على هذا الرمز يستطيع حذف كل المستودعات،
حذف الحساب، تغيير كلمة المرور، والوصول لكل شيء.

التصحيح:
1. حذف الرموز المكشوفة فوراً.
2. إنشاء رمز بصلاحيات محددة فقط.
3. التحقق من الصلاحيات قبل الاستخدام:
   - gh auth status | grep "Token scopes"

الصلاحيات الصحيحة: 'read:org', 'repo', 'workflow' فقط.

الدرس: Least Privilege يُطبَّق على المالك أيضاً، لا فقط على
الوكلاء. الأمان الذي نبنيه في النظام يجب أن يُطبَّق علينا أولاً.

الدرس الأعمق: أي رمز يُنشر في محادثة أو يُصوَّر = محروق.
يجب إلغاؤه فوراً، ليس "التأكد أولاً".

## الجلسة 9: V0.2a — كشف ثغرة العزل

### الخطأ #6: بوابة الذاكرة تمرر actions خارجية

السياق: عند اختبار بوابة memory/gate.py، اختبرنا رفض tool:python.
النتيجة: FAIL (لم يُرفض).

التشخيص: البوابة كانت تستخدم دور agent_high افتراضياً. هذا
الدور يملك tool:python عالمياً في السياسة. لذلك عندما تمرر
tool:python عبر البوابة، تُقبل.

الأثر: البوابة كانت تسمح بكل ما يملكه agent_high، ليس فقط
memory:*. هذا يكسر مبدأ العزل.

التصحيح: إضافة whitelist صريح (ALLOWED_ACTIONS) داخل gate.py.
أي فعل خارج memory:* يُرفض قبل الوصول إلى permission_gate.

الدرس: Defense in depth. طبقتان أفضل من طبقة. السياسة وحدها
لا تكفي — البوابة الوسيطة يجب أن تفرض قيودها الخاصة.

الدرس الأعمق: الاختبارات التي تفشل هي التي تحمي النظام. لو لم
نختبر tool:python، لما اكتشفنا الثغرة.

## الجلسة 10: log rotation

### الخطأ #7: rotation يكسر فحص السلامة

السياق: عند تنفيذ rotation.py لأول مرة، السجل الجديد
بدأ بـ prev_hash = آخر hash من الملف القديم. لكن
integrity.py يتوقع GENESIS_HASH ("0"*64) للسجل الأول.

النتيجة: "chain broken at seq 0".

التصحيح: جعل كل ملف مستقل. السجل الجديد يبدأ بـ "0"*64.
الربط بالقديم يُوثَّق في manifest.

الدرس: الفصل بين "سلامة ملف واحد" و"تاريخ كامل عبر
ملفات" مهم. الأول يومي، الثاني نادر. نُخَفِّض التعقيد
في الأكثر تكراراً.

## الجلسة 15: تصحيح Gate E — مراجعة نقدية

**التاريخ**: 2026-09-15
**السياق**: مراجعة خارجية كشفت أن Gate E انتقل من ✗ (فشل)
في V0.1 إلى "مؤجل" في V0.2/V0.3 بدون تبرير نصي.

**الخطأ المنهجي**: هذا النمط يُعرف بـ "moving the goalposts".
تحريك خط النهاية بعد رؤية النتيجة. وهو بالضبط ما حذّرت منه
وثيقة QSRB_INTEGRATION.md.

**الحقيقة**: Gate E اختبر شيئاً لم يكن موجوداً في V0.1
(Functional Form لسلوك الذاكرة). المعامل لم يكن له معنى
في V0.1.

**القرار**: 
1. Gate E يُصنَّف: NOT_APPLICABLE_IN_V0.1 (ليس FAILED).
2. Gate E يُنقل إلى V0.2b (حيث يصبح Functional Form ممكناً).
3. سبب الانتقال يُوثَّق صراحة في GATES.md.

**الدرس**: "مؤجل" بدون سبب نصي = فشل مُخفي. الفشل الموثق
أفضل من التأجيل الغامض.

---

## J-0.6.1 — Duplicate-agent voting (2026-09-17)

**What happened**: during G0.19 test (H21), it was discovered that
`resolve()` in `agents/multi/consensus.py` does not prevent the same
`agent_id` from casting multiple votes. A single agent can satisfy
MIN_QUORUM alone.

**Why**: the original implementation counted votes by list length,
without checking for distinct agent_id values.

**Impact**: 4 of 20 attempts in G0.19 (i = 4, 9, 14, 19) were not
blocked. This is a real single-agent control vector.

**Fix planned**: add a distinct-agent-id check in `resolve()`, and
raise ConsensusError if duplicates are found.

**Test**: will be added as scenario 4 in G0.19 (rebuilt).

**Cost**: 25 minutes.

---

## J-0.6.2 — G0.19 test scenario 2 was mislabeled (2026-09-17)

**What happened**: scenario 2 in test_g019 treated a legitimate
weighted decision as an attack. compute_agent_1 (cap 2.0) vs
query_agent_1 + system (0.85 + 0.85 = 1.70) is a valid decision,
not a single-agent control attempt.

**Impact**: 4 of 20 attempts (i = 2, 7, 12, 17) were marked
"not blocked" but should have been counted as legitimate outcomes.

**Fix planned**: remove scenario 2 from the attack list. Keep it
as a separate test of correct weighted decision.

**Test**: will be reorganized in G0.19 (rebuilt).

**Cost**: 15 minutes.

---

## J-0.7.1 — resolve() accepts PENDING state (2026-09-20)

**What happened**: during V0.7.1 Red Team (G0.25, test T1),
it was discovered that `resolve()` in `agents/multi/consensus.py`
accepts a proposal whose state is `PENDING` (not `VOTING`).

The condition in V0.6 was:

    if proposal.state != ProposalState.PENDING and \
       proposal.state != ProposalState.VOTING:
        raise ConsensusError(...)

This allows a newly-created proposal to be resolved WITHOUT
entering the VOTING state. A proposer could bypass the voting
phase entirely.

**Why**: the original V0.6 code treated PENDING as a valid
state for resolve(). This was intended as "resolve a fresh
proposal that has no votes yet". But it opens a bypass.

**Impact**: severity MEDIUM. In practice, callers (coordinator)
always set state=VOTING before resolving. But the invariant
is not enforced at the protocol layer.

**Fix planned**: in V0.7.1.1 (emergency patch), change the
state check to REJECT PENDING in resolve(). Only VOTING and
terminal states are accepted. Also, add a guard: resolve()
cannot accept a proposal with zero votes and zero quorum path.

**Note**: this finding is logged BEFORE any fix, per
docs/OPENING.md. V0.7.1 gate G0.25 fails as designed.

**Test**: T1 in tests/gate_v07/test_g025_timing.py
currently returns False (not blocked) until fix.

**Cost estimate**: 20 minutes.

**Decision**: V0.7.1 is declared PARTIAL until fix.
V0.7.1.1 will be a patch release, followed by re-run of G0.25.

---

## J-0.7.2 — GPG setup not completed (2026-09-17)

**What happened**: attempted to set up GPG key for git commit
signing. Termux prompts for interactive key generation were
error-prone on mobile. The process was interrupted.

**Impact**: commits are NOT signed with GPG. They are signed
with git's own author identity only.

**Workaround**: rely on GitHub's verified-commits via HTTPS.

**Cost**: 20 minutes.

**Status**: accepted limitation. Documented here for honesty.

---

## J-0.7.3 — llama-cpp-python fails on Termux/Android (2026-09-17)

**What happened**: attempted to install llama-cpp-python for
V0.6a (LLM agent plan). The wheel was built successfully but
loading it raised RuntimeError("Unsupported platform").

**Root cause**: PyPI wheels for llama-cpp-python do not
support Android ARM64 at the platform-name level.

**Impact**: V0.6a (LLM) was abandoned. Pivoted to V0.6
(multi-agent without LLM).

**Alternative considered**: ctransformers, ollama. All have
similar platform limitations.

**Cost**: 2 hours.

**Status**: abandoned. Preserved as docs/FREEZE_v0.6_LLM_ABANDONED.md.

---

## J-0.7.4 — Heredoc typo incident (2026-09-20)

**What happened**: during V0.7.2 work, a documentation
snippet was pasted directly into Termux instead of being
wrapped in a heredoc. Bash attempted to execute the text
as commands, producing "command not found" errors.

**Impact**: no files changed, no state corruption. Screen
noise only.

**Lesson**: always verify paste destination. Heredoc content
must be inside `cat > file << 'EOF' ... EOF`.

**Cost**: 5 minutes.

**Status**: documented as a process lesson.

---

## J-0.7.5 — Test typo s2_fake_agent (2026-09-20)

**What happened**: in test_g023_sybil.py, a function was
defined as `s2_fake_agent_not_registered` but referenced
as `s2_fake_agent_not_in_registry` in the attacks list.

**Impact**: NameError on first run of the test.

**Fix**: safe patch (replace + assert count == 1).

**Lesson**: naming inconsistencies are caught early by
running tests immediately after writing. The discipline
of "test immediately" prevented any delay.

**Cost**: 5 minutes.

**Status**: fixed. Pattern captured in safe-patch methodology.

---

## J-0.7.6 — Runner variance between runs (2026-09-20)

**What happened**: performance measurements on the same
device differed between runs:
- Cycle median: 0.833 ms → 1.112 ms (+34%)
- Throughput median: 1131/s → 897/s (-21%)

**Root cause**: Android background processes, CPU thermal
state, screen on/off, GC timing. Not controllable from
within Termux.

**Impact**: numbers are NOT stable. Thresholds still hold
by large margins, but absolute numbers should not be
quoted as if they were fixed.

**Mitigation**: documented in PERFORMANCE_v0.6.md section 5
("Honesty about Variance"). Thresholds are set with wide
margins (11x - 120x) precisely because of this.

**Cost**: 30 minutes of analysis.

**Status**: documented. Accepted limitation of single-device
measurement.

---

## J-0.8.1 — V0.5 agents fail on fresh clone (2026-09-22)

**What happened**: tested `git clone` + `run_all.py` on a
fresh Google Colab environment. 3 gates failed:

    G0.31 Real FileAgent      FAILED (0/10)
    G0.32 Real ComputeAgent   FAILED (0/10)
    G0.33 Real QueryAgent     FAILED (0/10)

All other gates passed (13/16 closed).

**Root cause**: V0.5 agents require 3 files that are
excluded from git by `.gitignore` for safety:

    identity/owner_key.priv    (owner private key)
    identity/root_state.json   (root state)
    audit/audit.jsonl          (audit chain log)

On Termux (original dev device), these files exist locally
and V0.5 agents work. On a fresh clone (Colab, new device),
they are missing. `governed_action_v05` fails when it tries
to sign or verify actions. `agent.act()` raises, and the
coordinator reports "read_exec_failed".

**Impact**: MEDIUM-HIGH. The project claims reproducibility.
It is reproducible for V0.4, V0.6, V0.7.1, V0.7.2, V0.7.4
(13/16 gates), but NOT for V0.5 agents (V0.7.3 phase).
This is a real gap that a fresh-clone test would find
in seconds.

**Severity**: This is a Reproducibility failure — a
foundational property in scientific work.

**Fix plan** (V0.7.5 - Fresh Clone Support):

1. Add a `bootstrap.py` script that:
   - Generates a fresh owner key if missing
   - Creates an empty audit.jsonl if missing
   - Registers owner + agents into subjects.json
   - Prints the new owner fingerprint

2. Update run_all.py to call bootstrap.py first.

3. Update README.md with "Fresh clone setup" section.

4. Document that `owner_key.priv` from the original device
   is NOT distributable, and that a fresh key is expected.

5. Add a new test: `test_g038_fresh_clone_setup.py` that
   verifies bootstrap works on a clean checkout.

**Cost estimate**: 2-4 hours.

**Status**: documented. Fix is planned for V0.7.5.

**Scientific note**: this finding validates the decision
to run external tests. Self-testing on the dev device hid
this defect. External environments expose it. This is
exactly why reproducible scientific work requires
independent verification.

---

## J-0.8.3 — seed/root.py assumes Path.home() (2026-09-22)

**What happened**: during external testing on Google Colab,
`bootstrap.py` failed at the very first step
(`step_owner_key`), raising:

    RuntimeError: مفتاح المالك موجود مسبقاً.

even after manually deleting `identity/owner_key.*`.

**Root cause**: `seed/root.py` (V0.1) uses an absolute path:

    KERNEL_DIR = Path.home() / "governance_kernel"
    IDENTITY_DIR = KERNEL_DIR / "identity"

This assumes the repository is always at
`$HOME/governance_kernel`. On Termux this is true.
On Colab, the repository is at `/content/governance-kernel`,
so `Path.home()` = `/root`, and the target directory is
`/root/governance_kernel`.

As a result:
1. First run: `mkdir` creates `/root/governance_kernel/identity/`
   and writes keys there.
2. Second run: `OWNER_KEY_PRIV.exists()` at `/root/governance_kernel/`
   is True -> RuntimeError.
3. Keys are written OUTSIDE the repository. V0.5 agents
   look for them inside the repo -> still fail.

**Impact**: HIGH. This affects:
- Google Colab
- Any machine where the repo is not at `$HOME/governance_kernel`
- Reproducibility across environments

**Fix planned** (V0.7.6 - Path Portability):

The `Path.home()` pattern is a foundational assumption in
V0.1. Touching it would violate the Kernel Untouched rule.

**Alternative fix**: teach `bootstrap.py` to work around it:
- Detect the actual repo root via `Path(__file__).parent`
- If `Path.home() / "governance_kernel"` differs from repo root,
  print a clear WARNING
- Do NOT call `root.generate_owner_key()` in that case
- Instead: generate the key by calling `cryptography` directly,
  using the repo-local path

This keeps V0.1 untouched while making `bootstrap.py`
portable.

**Cost estimate**: 1-2 hours.

**Status**: documented. Fix planned for V0.7.6.

**Scientific note**: this is the SECOND reproducibility
gap found by external testing. Both were invisible on the
dev device. This strongly validates the decision to test
on external environments BEFORE publishing.

Only a Red Team from outside can find this class of defects.

---

## J-0.8.4 — policy_store.py also uses Path.home() (2026-09-22)

**What happened**: after fixing seed/root.py (J-0.8.3),
test_g031 on Colab still failed with:

    FileNotFoundError: missing policy:
    /root/governance_kernel/policy/policies/default.yaml

The correct path on Colab is
`/content/governance-kernel/policy/policies/default.yaml`.
`/root/...` is the wrong location.

**Root cause**: `policy/policy_store.py` uses the same
`Path.home()` pattern that J-0.8.3 identified in `seed/root.py`:

    KERNEL_DIR = Path.home() / "governance_kernel"
    POLICY_FILE = KERNEL_DIR / "policy" / "policies" / "default.yaml"

**Impact**: HIGH. Same class of defect as J-0.8.3.
Any fresh clone (Colab, external machine, CI) fails to
load the policy, and thus V0.5 agents fail.

**Scope of the issue**: an audit is required across the
entire V0.1-V0.4 codebase for other Path.home() usages.
Candidate files (to be verified):

    policy/policy_store.py        (confirmed)
    policy/policy_engine.py       (candidate)
    seed/root.py                  (fixed in V0.7.6)
    control/*                     (candidate)
    audit/*                       (candidate)
    authorization/*               (candidate)

**Fix planned** (V0.7.7 - Path Portability phase 2):

Audit the whole codebase. Replace every
`Path.home() / "governance_kernel"` with a __file__-based
path. This is a second explicit deviation from Kernel
Untouched, and it will be documented.

**Cost estimate**: 2-3 hours.

**Status**: documented. Fix planned for V0.7.7.

**Scientific note**: this is the FOURTH reproducibility
gap found by external testing. It was HIDDEN by the fact
that Termux has the repo at $HOME/governance_kernel, so
Path.home() works there. External environments (Colab,
CI, any developer machine) will expose it immediately.

The lesson: a single Path.home() fix is not enough.
Portability requires a systematic audit.

---

## J-0.8.5 — Full audit: 7 files use Path.home() (2026-09-22)

**What happened**: after J-0.8.4, a systematic grep across
the whole codebase found ALL Path.home() usages.

**Full list (7 files)**:

V0.1 files (audit/, policy/, authorization/, control/):
1. audit/append_only_log.py       line 8
2. audit/integrity.py             line 7
3. policy/policy_store.py         line 8
4. authorization/branch_registry.py line 10
5. control/kill_switch.py         line 10
6. control/resource_governor.py   line 9

V0.5 file:
7. agents/invariant_checker.py    line 17 (SANDBOX_ROOT)

**What is already correct** (V0.2a, V0.3):
- audit/rotation.py              uses _kernel (from __file__)
- authorization/subject_registry.py uses _root (from __file__)
- memory/episodic/event_log.py   uses _kernel
- memory/semantic/graph.py       uses _kernel
- seed/root.py                   FIXED in V0.7.6

**Analysis**: V0.1 used Path.home() consistently. V0.2a and
V0.3 corrected this pattern. V0.5 regressed (invariant_checker).

**Fix planned** (V0.7.7 - Path Portability phase 2):

For each of the 7 files, replace:

    KERNEL_DIR = Path.home() / "governance_kernel"

with:

    KERNEL_DIR = Path(__file__).resolve().parent.parent

For agents/invariant_checker.py:

    SANDBOX_ROOT = Path.home() / "governance_kernel" / "agents_sandbox"
  ->
    SANDBOX_ROOT = Path(__file__).resolve().parent.parent / "agents_sandbox"

Note: agents/invariant_checker.py is a V0.5 file. Fixing it
also deviates from Kernel Untouched (V0.5 was frozen).
This deviation is documented here.

**Impact of fixing**: on Termux, no behavior change (same
path). On Colab/external machines, all 7 files now work.

**Cost estimate**: 3-4 hours.

**Status**: documented. Fix planned for V0.7.7.

**Scientific note**: this is the FIFTH reproducibility gap
found by external testing, and the most important.

Why: it is not a single bug. It is a SYSTEMATIC pattern
spread across 7 files. The fact that it went undetected
for 7 versions (V0.1 through V0.7) reveals that the entire
"works on my machine" assumption was never tested.

The audit turned a local workaround into a global fix.
This is what external testing is for.

---

## J-0.8.6 — Policy signature invalid after bootstrap (2026-09-22)

**What happened**: after V0.7.7, on a fresh Colab clone,
test_g031 failed with:

    RuntimeError: policy signature INVALID — possible tamper

traceback points to:
    policy/policy_store.py:39 load()
    -> root.verify(_hash_policy(text), sig) fails

**Root cause**: default.yaml.sig is committed to Git and
was signed with the ORIGINAL owner key from the Termux
device. When a fresh clone runs bootstrap.py, a NEW owner
key is generated. The old signature (from Git) does not
match the new key.

Result: policy_store.load() raises RuntimeError on every
fresh clone.

**Impact**: HIGH. This is the THIRD defect in the fresh
clone path:
- J-0.8.1: bootstrap.py missing
- J-0.8.3: seed/root.py Path.home()
- J-0.8.5: 7 files Path.home()
- J-0.8.6: default.yaml.sig from old key

Without a fresh clone, this is invisible because Termux
keeps the same key forever.

**Fix planned** (V0.7.8 - Bootstrap resigning):

In bootstrap.py, after generating the new owner key:
  1. Detect that default.yaml.sig exists but is invalid
  2. Re-sign default.yaml with the new key
  3. Overwrite default.yaml.sig

This is safe: the policy CONTENT is unchanged. Only the
signature is regenerated.

Additionally, G0.34 (V0.5 Untouched) must be updated:
- V0.7.7 modified agents/invariant_checker.py
- This is a documented deviation (see FREEZE_v0.7.7)
- Add invariant_checker.py to G0.34's ALLOWED_EXCEPTIONS
- Document J-0.8.6

**Cost estimate**: 1-2 hours.

**Status**: documented. Fix planned for V0.7.8.

**Scientific note**: the fresh-clone path has more
defects than expected. Each defect was hidden by the
Termux assumption that "the repo is always at $HOME and
the key is always the original key". External testing
revealed them all.

This is the SIXTH reproducibility gap found by external
testing. The pattern is now clear:
- Every assumption about the environment is a potential
  reproducibility defect.
- Only external testing reveals them.

---

## J-0.8.7 — Empty audit.jsonl breaks append (2026-09-22)

**What happened**: after V0.7.8, fresh Colab clone runs
bootstrap.py which creates `logs/audit.jsonl` as an EMPTY
file (0 bytes). Then test_g031 calls agent.act() which
flows into audit.append(). That raises:

    File "audit/append_only_log.py", line 72, in append
        seq = last["seq"] + 1
    TypeError: 'NoneType' object is not subscriptable

**Root cause**: `_read_last()` returns None for an empty
file. `append()` assumes `_read_last()` always returns a
dict. On first-ever append to a fresh (empty) log, this
assumption fails.

**Why this was hidden before V0.7.5**:
- On Termux, `logs/audit.jsonl` was NEVER empty.
- It existed with records (from V0.1 genesis).
- `bootstrap.py` (V0.7.5) creates an empty file to satisfy
  the "file exists" check.
- This makes the first append crash.

**Impact**: HIGH. V0.5 agents cannot run on any fresh
clone because every action tries to append to the log.
This is the SEVENTH reproducibility gap found by
external testing.

**Fix planned** (V0.7.9):

Modify `audit/append_only_log.py::_read_last()` to return
a synthetic genesis record if the file is empty or
missing:

    if file is empty:
        return {
            "seq": 0,
            "ts": 0,
            "prev_hash": "0" * 64,
            "kind": "genesis_synthetic",
            "data": {},
            "hash": "0" * 64,
        }

This makes `append()` work correctly on empty logs.
Alternatively, `bootstrap.py` should write a genesis
record instead of creating an empty file.

The preferred fix is in `_read_last()`, because it makes
the log module self-healing regardless of how the file
was created.

**Cost estimate**: 30-45 minutes.

**Status**: documented. Fix planned for V0.7.9.

**Scientific note**: this is the SEVENTH reproducibility
gap. The pattern continues: each fix exposes a new
assumption that only external testing reveals. The
"fresh clone" path has been a cascade of hidden
assumptions about local state.

---

## J-0.8.8 — The "Zero-Dependency" claim is inaccurate (2026-09-23)

**What happened**: while preparing a GitHub Actions workflow,
I checked exactly which packages are imported across the
codebase. Found:

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

in seed/root.py. `cryptography` is NOT part of the Python
standard library. It is a third-party C-extension package.

**Impact**: MEDIUM-HIGH. The project has claimed
"zero external dependencies" and "Python standard library
only" in multiple places (README.md, OPENING.md, CHARTER.md,
FREEZE files, release notes). This claim is not accurate.

Truth: the project has ONE external dependency
(`cryptography`), not zero.

**Why it was hidden**:
- On Termux, `cryptography` ships with the Python install.
- On Google Colab, `cryptography` is pre-installed.
- The project NEVER had to run `pip install cryptography`
  on any environment tested so far.
- Result: "zero dependencies" FELT true.

**Reality check**: on a bare Python install (e.g. GitHub
Actions ubuntu-latest with actions/setup-python), running
`python audit/integrity.py` would fail with
`ModuleNotFoundError: No module named 'cryptography'`.

**Fix plan** (documentation-only, no code change):

1. Document this in JOURNEY.md (this entry).
2. Update README.md: replace "Zero external dependencies"
   with an honest statement about the single dependency.
3. Update docs/OPENING.md: add a "Known dependencies"
   section under section 6 (Admission of limits).
4. Do NOT modify CHARTER.md — it is a founding document.
   Instead, add a note in OPENING.md that references
   the CHARTER's original aspiration.

**Cost estimate**: 30 minutes (documentation only).

**Status**: documented. Awaiting correction pass.

**Scientific note**: this is the EIGHTH finding in the
reproducibility/correctness series. The pattern continues:
even a well-documented project can carry claims that are
subtly false. External scrutiny (in this case, imagining
a GitHub Actions workflow) is what reveals them.

The original claim "zero-dependency" was aspirational.
Reality is "one-dependency, deliberately minimal, and
fully accounted for".

---

## J-0.8.9 — PyYAML is a second dependency (2026-09-23)

**What happened**: on the first GitHub Actions run, the
V0.5 job failed with:

    File "policy/policy_store.py", line 4, in <module>
        import yaml
    ModuleNotFoundError: No module named 'yaml'

The workflow installed `cryptography` but NOT `pyyaml`.

**Root cause**: `policy/policy_store.py` imports the
third-party package `yaml` (PyYAML). This is a second
external dependency, in addition to `cryptography`.

**Impact**: MEDIUM-HIGH. J-0.8.8 stated the project has
"exactly ONE external dependency". This was inaccurate.
The true count is TWO (and there may be more).

**Why it was hidden**: on Termux and Colab, `pyyaml` is
pre-installed. Like `cryptography`, it was invisible
until a truly clean environment tested it.

**Fix plan** (V0.7.11):

1. Document this in JOURNEY.md (this entry).
2. Update .github/workflows/test.yml:
   pip install cryptography pyyaml
3. Update README.md: 2 dependencies, list them explicitly
4. Update docs/OPENING.md: known dependencies now lists 2
5. Audit entire codebase for other third-party imports

**Dependencies now known**:
- cryptography (Ed25519 in seed/root.py)
- pyyaml (YAML parsing in policy/policy_store.py)

**Audit method**: grep for imports that are not stdlib.

**Cost estimate**: 1-2 hours (includes full audit).

**Status**: documented. Fix planned for V0.7.11.

**Scientific note**: this is the NINTH finding in the
J-0.8.x series. The pattern continues: a claim ("1
dependency") that felt true in two environments (Termux,
Colab) was proven false by a third (GitHub Actions).

This validates the decision to add CI. The only way to
find this class of defect is to test in a truly clean
environment. Each environment reveals what the previous
ones hid.

---

## J-0.8.10 — branches/registry.jsonl is not bootstrapped (2026-09-23)

**What happened**: second GitHub Actions run (after
V0.7.11 fix). V0.5 now reaches G0.13, but G0.13 fails:

    FAIL: file_agent_1 not registered
    FAIL: compute_agent_1 not registered
    FAIL: query_agent_1 not registered
    G0.13: 0/3 registered and verified
    V0.5 gates: 4/5 closed

G0.14, G0.15, G0.16, G0.17 all pass. Only G0.13 fails.

**Root cause**: `branches/registry.jsonl` is listed in
.gitignore (line: `branches/registry.jsonl`). On a fresh
clone, this file does not exist. No branches are
registered. G0.13 fails.

**Why it was hidden**:
- On Termux, `branches/registry.jsonl` exists since V0.1.
- On Colab, `bootstrap.py` did not register branches
  either — but the file may have been committed
  accidentally at some point, or the test on Colab
  passed for a different reason.
- Actually: on Colab, `bootstrap.py` writes to `logs/`,
  `identity/`, `authorization/subjects.json`, and the
  policy signature. It does NOT touch `branches/`.
  The G0.13 test on Colab was never seen failing because
  previous Colab runs may have been on checkouts that
  included a stale branches file, or the tests were not
  run in the exact same state.
- Result: this defect was invisible on Termux and
  appeared only on GitHub Actions, where the checkout
  is guaranteed clean.

**Impact**: HIGH. Fresh clones cannot run V0.5 fully
without manual registration.

**Fix plan** (V0.7.12):

Update `bootstrap.py` to register the three default
branches automatically, AFTER `step_subjects()`.

New step: `step_register_branches()`

Logic:
  - Import agents.register_agents
  - Call its main registration logic
  - Print a summary line

This reuses the existing V0.5 logic (no duplication).
It does NOT modify any V0.1-V0.5 code.

Alternatively, `run_all.py` could call
`agents/register_agents.py` before V0.5 tests. But
putting it in `bootstrap.py` is cleaner: bootstrap
becomes the single source of "fresh clone setup".

**Cost estimate**: 30 minutes.

**Status**: documented. Fix planned for V0.7.12.

**Scientific note**: this is the TENTH finding in the
J-0.8.x series. The pattern remains consistent: each
external environment reveals what previous environments
hid. GitHub Actions is the strictest environment so far
because it starts from a truly clean checkout.

The project now has evidence that:
- Termux: 19/19 (manual setup over time)
- Colab: 19/19 (after bootstrap)
- GitHub Actions: V0.5 partial (branches missing)

The gap is now precisely identified and fixable.


## J-0.8.11 — CI shallow clone hides v0.6-closed tag

**Discovered**: 2026-09-23, GitHub Actions run 35847336154,
  after v0.7.12 (commit 1198b37) pushed.

**Symptom**: V0.7 gates: 17/19 closed.
  - G0.34 V0.5 Untouched:   FAILED (could not diff)
  - G0.ZZ Kernel Untouched: FAILED

**Error in CI log**:
    ERROR running git diff: fatal: ambiguous argument
    'v0.6-closed': unknown revision or path not in the
    working tree.
    G0.34: FAILED (could not diff)

**Root cause**:
  .github/workflows/test.yml uses actions/checkout@v4 with
  no `fetch-depth` override. Default is fetch-depth: 1
  (shallow clone without tags). Gates G0.34 and G0.ZZ both
  run `git diff v0.6-closed HEAD` to verify protected files
  were not modified. In CI, the tag does not exist locally,
  so git diff fails.

**Why it was hidden**:
  - Termux: full clone, all tags present. 19/19.
  - Colab:  full clone / manual setup preserves history.
    19/19.
  - CI:     shallow clone (fetch-depth: 1), tags absent.
    Never reached before because until v0.7.12, V0.7 tests
    failed earlier (branches missing → V0.5 partial →
    downstream gates never exercised).

  Pattern "each fix reveals a deeper problem":
  fixing bootstrap (J-0.8.10) allowed V0.7 to run further,
  exposing the shallow-clone gap.

**Impact**: HIGH for reproducibility claim.
  - Claim "19/19 on 3 environments" is currently FALSE.
  - Reality: 19/19 on Termux + Colab; 17/19 on CI.
  - Fixable with 2 lines in CI config.

**Fix plan** (V0.7.13):

Modify .github/workflows/test.yml Checkout step:
    with:
      fetch-depth: 0
      fetch-tags: true

Alternative REJECTED: make G0.34 / G0.ZZ gracefully skip
when the tag is absent. These are real audit gates
(V0.5 byte-identical check). Weakening them to accommodate
a CI misconfiguration is backwards.

No kernel code touched. No gate logic touched.

**Cost estimate**: 10 minutes.

**Status**: CLOSED (2026-09-23).

  Verified on GitHub Actions run 35849426756
  (commit d2fc322): V0.7 gates 19/19 closed.
  V0.5 gates 5/5 closed. Full matrix green:
    - Termux:           5/5 + 19/19
    - GitHub Actions:   5/5 + 19/19
    - Colab:            5/5 + 19/19 (pre-v0.7.13)

  Repro claim updated: "19/19 on 3 environments" is
  now TRUE (was FALSE at the time this finding was
  discovered).

**Scientific note**: this is the ELEVENTH finding in the
J-0.8.x series. The chain of 11 findings in ~24 hours is
itself the strongest evidence that the reproducibility
claim required multi-environment testing.

Correction to prior claims:
  - Earlier: "19/19 on 3 environments" -> imprecise.
  - Now:     "19/19 on Termux + Colab; CI pending V0.7.13."


## J-0.8.14 — consensus/journal.jsonl grows unbounded

**Discovered**: 2026-09-23, Termux (during V0.7 runs)
**Class**: Resource leak / operational hygiene

**Symptom**:
  consensus/journal.jsonl = 23,098,288 bytes (23 MB)
                          92,493 lines
  Last modified: 2026-09-23 10:32

**Root cause**:
  - agents/multi/consensus.py:32
  - agents/multi/communication.py:21
  - agents/multi/coordinator.py:26
    All three define:
      _JOURNAL_PATH = Path(__file__).parent.parent.parent
                      / "consensus" / "journal.jsonl"
    Each writes to the same file. No rotation logic exists
    (grep for rotate/max_size/max_bytes/truncate returns nothing).

**Why it was hidden**:
  - On Termux: file grows silently across runs. No failure
    until filesystem pressure.
  - On CI/Colab: fresh clone. File never exists. Never grows.
  - No test asserts journal size.
  - No alert on growth.

**Impact**: MEDIUM.
  - Local Termux only: 23 MB after ~1 month. Linear growth.
  - CI/Colab: unaffected (fresh clones).
  - Risk of concurrent writes if 3 modules append simultaneously
    in a multi-process setup (not currently tested).
  - git add . previously would have pushed 23 MB — now
    mitigated by .gitignore (commit b3ad05c).

**Fix plan** (V0.7.14):

Option A — rotation in consensus module:
  - Add rotation when file exceeds N lines (e.g. 10,000)
  - Rotate to journal.jsonl.1, .2, ...
  - Keep max K archives

Option B — cap + truncate:
  - Truncate to last N lines when file exceeds threshold
  - Simpler but loses history

Option C — move to per-run file:
  - consensus/journal-<timestamp>.jsonl
  - Requires external cleanup

Recommended: A (rotation) for V0.8+; C for testing.
Decision deferred.

**Cost estimate**: 2 hours.

**Status**: PENDING. Documented only.

**Note**: The .gitignore fix (commit b3ad05c) prevented the
immediate risk of pushing 23 MB. But the underlying growth
problem remains on any long-running Termux instance.


## J-0.8.21 — bootstrap.py lacks memory branch registration

**Discovered**: 2026-09-23, Colab (extended testing session)
**Class**: Build reproducibility gap
**Related**: J-0.8.20 (Gate D needs 3 fixes)

**Symptom**:
  Fresh clone: `python bootstrap.py` runs successfully,
  but does not register the `memory` branch.
  `memory/gate.py` then fails with:
    RuntimeError: فرع 'memory' غير مسجّل
  The `memory_system` subject is also missing from
  `authorization/subjects.json`.

**Root cause**:
  bootstrap.py registered only:
  - owner + system + 3 agents (subjects)
  - file_agent_1, compute_agent_1, query_agent_1 (branches)
  It did NOT call memory/register_branch.py.
  It did NOT include memory_system in DEFAULT_SUBJECTS.

  Two layers:
  1. Missing step: register_memory_branch()
  2. Missing subject: memory_system (default in memory/gate.py:82)

**Why it was hidden**:
  - Termux: manual registration performed in V0.2a.
    registry.jsonl persists across sessions.
  - CI/Colab: fresh clone, but bootstrap never tested with
    memory-dependent tests.
  - No test in V0.4-V0.7 exercises the memory branch.

**Impact**: MEDIUM.
  - Affects fresh clones (CI, Colab).
  - Breaks Gate D (tests/gate_d_benchmark.py) entirely.
  - Does not affect V0.4, V0.5, V0.6, V0.7 (no memory usage).

**Fix plan** (V0.7.14):

1. Add "memory_system" to DEFAULT_SUBJECTS in bootstrap.py
   (role: system, trust: 0.9).
2. Add step_register_memory_branch() that:
   - Checks if "memory" is already registered (idempotent)
   - Calls memory/register_branch.py as subprocess
   - Prints [OK  ] or [SKIP] appropriately
3. Call step_register_memory_branch() in main() between
   step_register_branches() and step_policy_signature().

**Cost estimate**: 30 minutes.

**Status**: CLOSED (2026-09-24).

  Verified on Termux (idempotent SKIP case) and on
  simulated fresh clone (registry.jsonl deleted):
    [OK  ] branches: 3 registered, 0 skipped
    [OK  ] memory branch registered
  Result: 4 branches registered (was 3).
  subjects.json: 9 subjects (was 8).
  V0.5: 5/5 CLOSED.
  V0.7: 19/19 CLOSED.

**Side note**: A local-only 'mem_branch' entry (V0.2a,
2026-09-12) exists in Termux's registry.jsonl. It is not used
by any code and is not present on fresh clones. After the
fresh-clone simulation, the registry contains exactly
4 branches (file_agent_1, compute_agent_1, query_agent_1,
memory). No cleanup of Termux's local mem_branch was
performed; it was removed automatically by the simulation.


## J-0.8.28 — G0.ZZ forbids modifying authorization/, but bootstrap.py must modify authorization/subjects.json

**Discovered**: 2026-09-24, GitHub Actions run 36025304378
**Class**: Scope Lock conflict
**Related**: J-0.8.21 (bootstrap memory branch)

**Symptom**:
  After commit 0404d22 (v0.7.14, J-0.8.21 fix), CI fails:
    G0.ZZ Kernel Untouched    FAILED
    V0.7 gates: 18/19 closed
  Local Termux: G0.ZZ returns exit code 1 after the fix.

**Root cause**:
  Two requirements in direct conflict:

  1. FREEZE_v0.7.md Section 0 lists "authorization/" as protected.
     G0.ZZ enforces this via `git diff v0.6-closed HEAD`.

  2. bootstrap.py (v0.7.14, from J-0.8.21) must add
     "memory_system" to authorization/subjects.json so that
     memory/gate.py default subject resolution works on
     fresh clones.

  Result: bootstrap.py modifies a protected file -> G0.ZZ fails.

  The conflict existed implicitly since V0.5 (bootstrap.py has
  always managed subjects.json) but was hidden because:
  - Up to v0.7.13, subjects.json contained only pre-V0.5 subjects
    (owner, system, agents). These were committed once in V0.4.1
    (cda932d, 1f26943) and never changed since.
  - V0.7.14 is the first commit to add a new subject after
    v0.6-closed.

**Why it was hidden**:
  - G0.ZZ compares v0.6-closed to HEAD.
  - No subject had been added to subjects.json since V0.4.1.
  - Therefore the file appeared "untouched" for 3 versions.
  - v0.7.14's addition of memory_system broke this appearance.

**Impact**: HIGH for CI, MEDIUM for runtime.
  - CI now fails at V0.7 (18/19 instead of 19/19).
  - V0.5, V0.6 unaffected.
  - Termux runs after the fix fail G0.ZZ locally.
  - The kernel itself is unchanged — only a data file.

**Fix plan** (v0.7.15):

1. Add "authorization/subjects.json" to ALLOWED_EXCEPTIONS in
   tests/gate_v07/test_g0ZZ_kernel_untouched.py.
2. Document the deviation in docs/FREEZE_v0.7.md Section 0.
3. Create docs/FREEZE_v0.7.15.md with the deviation declaration.

The exception is narrow:
  - ONE file only: authorization/subjects.json
  - Additive only: new subjects, never removals or edits
  - Required for bootstrap correctness on fresh clones

**Cost estimate**: 30 minutes.

**Status**: documented. Fix planned for v0.7.15.

**Scientific note**: This is the THIRD scope-lock conflict in the
J-0.8.x series (after J-0.8.3/J-0.8.5 which required
ALLOWED_EXCEPTIONS for Path.home files). Each conflict reveals
that "kernel untouched" is not a binary but a moving boundary
that must be re-declared whenever a new legitimate need appears.
The exception mechanism (ALLOWED_EXCEPTIONS) exists precisely
for this. Without it, no legitimate maintenance would be
possible after v0.6-closed.


## J-0.8.12 — README claims "Six gates closed" with no traceable source

**Discovered**: 2026-09-23, extended review session
**Class**: Documentation staleness
**Related**: J-0.8.13, J-0.8.17, J-0.8.18

**Symptom**:
  README.md line 7 stated:
    "Six gates closed. 54/54 attacks blocked. PRI = 1.0000."
  The number "Six" was not traceable to any source:
  - GATES.md documents 10 conceptual gates (Gate 0 to H), not six.
  - V0.4 has 5 attacks (a1-a5) + __init__.py = 6 files,
    but "attacks" are not "gates".
  - V0.5: 5 gates.
  - V0.6: 5 gates.
  - V0.7: 19 gates.
  - Sum V0.5-V0.7 = 29 gates.
  The claim appeared once in README, never updated after V0.5.

**Root cause**:
  The line was written during V0.5 era (README last updated
  2026-09-15, before V0.6 and V0.7). The number "Six" was
  likely an approximation that was never updated. V0.6 and
  V0.7 (10 commits since) added no README updates for the
  status line.

**Why it was hidden**:
  - No test asserts README content.
  - CI does not check documentation.
  - The claim appeared plausible at a glance.

**Impact**: MEDIUM for external credibility.
  - A reader sees "Six gates" and infers a small project.
  - Reality: 29 numbered gates across V0.5-V0.7.
  - Discrepancy: 23 gates unaccounted.
  - README is the first thing visitors see.

**Fix plan** (this commit):

1. Line 7 rewritten:
     BEFORE: Six gates closed. 54/54 attacks blocked. PRI = 1.0000.
     AFTER:  29 gates closed (V0.5-V0.7). 54/54 attacks blocked (V0.4).
             PRI = 1.0000.
2. Status table extended with V0.6 and V0.7 rows.
3. Added "Full V0.7 report" line.
4. Footer updated to "Last updated: 2026-09-25 — V0.7.15".

Out of scope (separate findings):
  - README claims "16 architectural patterns" (real: 18).
  - README references tests/gate_v03/ which does not exist.
  - README quick start says "cd governance_kernel" (should be
    "governance-kernel").
  - README says "Latest DOI (V0.6)" but V0.7 has no DOI yet.

**Cost estimate**: 30 minutes.

**Status**: CLOSED (2026-09-25).

  Committed in v0.7.15 (README update).
  README now reflects V0.1-V0.7 closure status.

**Scientific note**: 28th finding in the J-0.8.x series.
It reveals a pattern: README is a "front door" forgotten
during development. Documentation debt accumulates silently.
Fix requires discipline of re-checking README after each
version bump.

## J-0.8.29 — README claims "16 architectural patterns"; actual count is 18

**Discovered**: 2026-09-25, during J-0.8.12 fix
**Class**: Documentation staleness
**Related**: J-0.8.12 (README number traceability)

**Symptom**:
  README.md line 85 states:
    "PATTERNS.md 16 architectural patterns"
  Actual count in docs/PATTERNS.md: 18 patterns
  (P-L1 to P-L5 = 5, P-Q1 to P-Q13 = 13).

**Root cause**:
  README was last updated 2026-09-15 (V0.5 era). The count
  was likely correct then. Two patterns were added after
  (P-Q12, P-Q13 in V0.7.4), but README never updated.

**Impact**: LOW.
  - Underreports by 2 patterns.
  - Appears alongside "Six gates" (now fixed) as further
    evidence of stale front-matter.

**Fix plan**: change "16" to "18" in README line 85. One word.

**Cost estimate**: 1 minute.

**Status**: CLOSED (2026-09-26). README line 89 now says "18".

## J-0.8.30 — README architecture tree references non-existent tests/gate_v03/

**Discovered**: 2026-09-25, during J-0.8.12 fix
**Class**: Documentation inaccuracy
**Related**: J-0.8.12

**Symptom**:
  README.md line 100 (Architecture tree) lists:
    "gate_v03/          G0.7, G0.9"
  But tests/gate_v03/ does not exist. V0.3 test files are in
  the repository root:
    tests_gate_v03_separation_smoke.py
    tests_gate_v03_six_combinations.py
  They were never moved to tests/ when later versions created
  tests/gate_v04/, gate_v05/, gate_v06/, gate_v07/.

**Root cause**:
  V0.3 (Separation) predates the tests/gate_vN/ convention
  introduced in V0.4. V0.3 test files remained in the root.
  README was written with a planned but never-executed move.

**Impact**: LOW.
  - Visitor may look for tests/gate_v03/ and fail.
  - Two V0.3 tests are effectively orphaned from the standard
    test tree.

**Fix plan**:
  Option A: update README to list the correct root paths.
  Option B: move the two files into tests/gate_v03/ (requires
            import path adjustments + G0.ZZ review).

**Resolution**: Option A adopted. Line removed from README
  Architecture tree (no tests/gate_v03/ entry).

**Status**: CLOSED (2026-09-26).

## J-0.8.31 — README quick start uses wrong directory name

**Discovered**: 2026-09-25, during J-0.8.12 fix
**Class**: Documentation inaccuracy
**Related**: J-0.8.12

**Symptom**:
  README.md line 141 (Quick start):
    git clone https://github.com/mohamedaitzaouit84-hue/governance-kernel
    cd governance_kernel
  But clone creates directory "governance-kernel" (with hyphen),
  not "governance_kernel" (with underscore). Following the
  README verbatim causes "No such file or directory".

**Root cause**:
  The underscore name "governance_kernel" is the intended Python
  package name (not yet published as an SDK). The clone directory
  uses the repository name with a hyphen. README mixed the two.

**Impact**: LOW but annoying.
  - Copy-pasting the quick start fails on step 2.
  - First impression for a new user is a broken command.

**Fix plan**: change "cd governance_kernel" to
  "cd governance-kernel". One character.

**Cost estimate**: 1 minute.

**Status**: CLOSED (2026-09-26). README line 144 now says "cd governance-kernel".

## J-0.8.13 — HANDOVER claims "1 dependency"; code imports 2

**Discovered**: 2026-09-23, extended review session
**Class**: Documentation staleness
**Related**: J-0.8.8 (zero-dependency), J-0.8.9 (PyYAML)

**Symptom**:
  HANDOVER (original, pre-2026-09-23) stated:
    "1 dependency (cryptography, for Ed25519)"
  Code imports:
    - cryptography (in seed/root.py)
    - pyyaml (in policy/policy_store.py,
              authorization/policy_extension.py)
  Total: 2 external dependencies, not 1.

**Root cause**:
  The original count missed pyyaml. J-0.8.8 fixed
  "zero" to "one" (cryptography). J-0.8.9 fixed
  "one" to "two" (adding pyyaml).

**Why it was hidden**:
  - pyyaml was installed alongside cryptography in
    every environment tested (Termux, Colab, CI).
  - No test isolated which package was needed.
  - The original count was never automated.

**Impact**: LOW.
  - README was fixed by v0.7.11 (2 dependencies).
  - HANDOVER was rewritten 2026-09-23 with correct
    count (2 dependencies).
  - No active claim of "1 dependency" remains in
    user-facing documentation.

**Status**: CLOSED (2026-09-26). Verified no active
inaccurate claims.

  Remaining mentions of "single dependency" are
  historical:
  - docs/FREEZE_v0.7.10.md:63 — written 2026-09-23
    before v0.7.11 (PyYAML correction). Frozen
    documents are immutable.
  - docs/JOURNEY.md:785 — text of J-0.8.8, written
    before J-0.8.9 discovered pyyaml. Historical
    record.

  Both are correct in their historical context.
  No edits needed.

**Cost estimate**: 0 (verified, no fix required).

**Scientific note**: This finding turned out to be
already-resolved by the chain J-0.8.8 -> J-0.8.9 ->
v0.7.11 -> HANDOVER rewrite. It demonstrates that
finding lists can lag behind reality. Periodic
re-verification prevents stale findings.

## J-0.8.16 — GATES.md application table stops at V0.3

**Discovered**: 2026-09-23, extended review session
**Class**: Documentation staleness
**Related**: J-0.8.12 (README), J-0.8.13 (dependency count)

**Symptom**:
  docs/GATES.md documents 10 conceptual gates
  (Gate 0 -> Gate H) with an application table:

    | Gate  | V0.1 | V0.2 | V0.3 |
    | Gate 0|  yes | req  | req  |
    ...

  The table stops at V0.3. No V0.4, V0.5, V0.6, V0.7 rows.

**Root cause**:
  V0.1 -> V0.3 used the Gate 0 -> H system (10 named gates).
  Starting with V0.4, the project switched to numbered gates
  (G0.13 -> G0.17 for V0.5, etc.). GATES.md was never updated
  to reflect the new system.

  Two gate systems now coexist:
  - Gate 0 -> H: conceptual, V0.1 -> V0.3 (documented in
    GATES.md)
  - G0.x: numbered, V0.4 -> V0.7 (documented in
    tests/gate_v0X/run_all.py and docs/GATES_v0.X_report.md)

**Why it was hidden**:
  - GATES.md is referenced by FREEZE_v0.2 and FREEZE_v0.3
    only. No post-V0.3 document references it.
  - The new system (G0.x) has its own documentation.
  - No test asserts GATES.md content.

**Impact**: MEDIUM for external readers.
  - A visitor reading GATES.md sees only V0.1 -> V0.3.
  - May infer the project stopped at V0.3.
  - The actual gate count (29) is in README and
    GATES_v0.X_report.md, not in GATES.md.

**Fix plan** (this commit):

Add a new section at the end of GATES.md:

    ## The New System (V0.4 -> V0.7)

    Starting with V0.4, Gate 0 -> H was replaced with
    numbered gates G0.x. The table above applies to
    V0.1 -> V0.3 only.

    [table of V0.4 -> V0.7 gates]

    Full documentation:
      tests/gate_v04/run_all.py
      tests/gate_v05/run_all.py
      ...
      docs/GATES_v0.5_report.md
      ...

This preserves GATES.md as a historical document while
clarifying the current state for readers.

**Cost estimate**: 15 minutes.

**Status**: documented. Fix planned for this commit.

**Scientific note**: This is another example of
"documentation drift" (see J-0.8.12). When a project
changes its internal methodology, old documents that
remain in the repo become misleading. The fix is not
to rewrite them but to add a bridge that points to
the new reality.

## J-0.8.17 — HANDOVER code-line count (5,500) vs reality (9,218)

**Discovered**: 2026-09-23, extended review session
**Class**: Documentation inaccuracy
**Related**: J-0.8.18 (findings count), J-0.8.12 (README)

**Symptom**:
  Original HANDOVER (pre-2026-09-23) stated:
    "~5,500 code lines"
  Actual count via:
    find . -name "*.py" -not -path "./.git/*" | xargs wc -l
  Result: 9,218 lines (2026-09-23).
  Underreport: ~3,700 lines (67% discrepancy).

**Root cause**:
  The "5,500" figure was written during an early version
  and never updated. It may have counted only "logic lines"
  (excluding tests/) or been an approximation. The actual
  count includes tests/ (which is the largest single
  directory).

  Breakdown (2026-09-26):
    tests/         4,618
    agents/        1,841
    memory/          990
    authorization/   377
    kernel/          354
    audit/           341
    root *.py        420
    control/         126
    policy/          110
    seed/             91
    tools/             0
    -----
    Total:         9,268

**Why it was hidden**:
  - No test asserts code size.
  - The original number was plausible when the project
    was smaller.
  - External review (listing all .py files) revealed
    the gap.

**Impact**: LOW.
  - HANDOVER was rewritten 2026-09-23 (8eaccc9) without
    the "5,500" claim. The variable number was removed
    deliberately (rule: HANDOVER carries no variable
    numbers).
  - The number only appears in pending-findings list
    (as documentation) and in ADDENDUM_2026-09-23
    (historical record).

**Status**: CLOSED (2026-09-26).

  The original claim is not present in the current
  HANDOVER. Actual count (9,268 as of 2026-09-26) is
  verifiable via wc -l. The +50 difference since
  2026-09-23 is explained:
    - bootstrap.py: +46 (v0.7.14 memory branch)
    - test_g0ZZ_kernel_untouched.py: +4 (v0.7.15)

**Cost estimate**: 0 (verified, no fix required).

**Scientific note**: This is the second finding in the
J-0.8.x series (after J-0.8.13) that was already
resolved by a later action. The HANDOVER rewrite
(8eaccc9) eliminated all variable numbers from
HANDOVER. What remained is documentation of the
finding itself. Periodic re-verification (this entry)
confirms the resolution.

## J-0.8.18 — HANDOVER findings count ("14") vs actual (18+)

**Discovered**: 2026-09-23, extended review session
**Class**: Documentation inaccuracy
**Related**: J-0.8.17 (code-line count), J-0.8.12 (README)

**Symptom**:
  Original HANDOVER (pre-2026-09-23) stated:
    "14 findings موثقة (J-0.6.1 to J-0.8.8)"
  Actual heading count in docs/JOURNEY.md at that time:
    J-0.6.x: 2
    J-0.7.x: 6
    J-0.8.x: 10
    -----
    Total:   18 headings
  Not 14.

**Root cause**:
  The "14" figure was likely an approximation written when
  fewer findings existed. New findings (J-0.8.9 onward) were
  added without updating the count. The original HANDOVER
  was not re-verified after each session.

**Why it was hidden**:
  - No test asserts JOURNEY heading count.
  - The HANDOVER summary looked plausible at a glance.
  - External review (grep -c "^## J-") revealed the gap.

**Impact**: LOW.
  - HANDOVER was rewritten 2026-09-23 (8eaccc9) without
    the "14" claim.
  - The number appears only in:
    - pending-findings list (documentation)
    - ADDENDUM_2026-09-23 (historical record)
    - ADDENDUM_2026-09-24 ("14 findings pending" as of that
      session's date — accurate historically)

**Status**: CLOSED (2026-09-26).

  Current heading count (2026-09-26):
    J-0.6.x: 2
    J-0.7.x: 6
    J-0.8.x: 20
    -----
    Total:   28 headings
  Verified via: grep -c "^## J-" docs/JOURNEY.md

  Note: ADDENDUM_2026-09-24 states "14 findings pending" as
  of 2026-09-24. This was accurate on that date. ADDENDUMs
  are historical session records and are not retroactively
  updated.

**Cost estimate**: 0 (verified, no fix required).

**Scientific note**: This is the third finding in the
J-0.8.x series (after J-0.8.13 and J-0.8.17) that was
already resolved by a later action. All three point to the
same lesson: variable numbers in documents become stale.
The HANDOVER rewrite eliminated them; only the historical
records remain, and those are accurate in their context.


## J-0.8.32 — Flat imports prevent SDK / pip install

**Discovered**: 2026-09-26, SDK test on Colab
**Class**: Architecture / Package structure
**Related**: SDK roadmap (ADDENDUM 2026-09-23)

**Symptom**:
  After `pip install .` succeeds (wheel built, installed
  to site-packages), importing modules fails:

    $ python -c "import authorization"
    ModuleNotFoundError: No module named 'authorization'

    $ python -c "from agents.multi.coordinator_v2 import CoordinatorV2"
    File "site-packages/agents/base_agent.py", line 24
      import governed_action_v05 as governed_action
    ModuleNotFoundError: No module named 'governed_action_v05'

  71 flat imports across the codebase rely on sys.path
  manipulation performed only by:
    - bootstrap.py
    - tests/gate_v07/run_all.py

  After pip install, no entry point manipulates sys.path.
  Every flat import fails.

**Examples of flat imports**:
  agents/register_agents.py:23: import branch_registry
  agents/register_agents.py:24: import root
  agents/register_agents.py:25: import append_only_log
  agents/base_agent.py:24:      import governed_action_v05
  agents/base_agent.py:25:      import kill_switch
  agents/base_agent.py:26:      import append_only_log
  seed/genesis.py:5:            import root
  policy/policy_engine.py:6:    import policy_store
  policy/policy_engine.py:7:    import subject_registry
  memory/gate.py:18:            import kill_switch
  memory/gate.py:21:            import branch_registry
  memory/semantic/graph.py:26:  import gate
  ... (71 total)

**Root cause**:
  The project has always been run from its repository root.
  bootstrap.py and tests/gate_v07/run_all.py do:
    sys.path.insert(0, str(REPO / "seed"))
    sys.path.insert(0, str(REPO / "audit"))
    sys.path.insert(0, str(REPO / "authorization"))
  This makes `import kill_switch` work (flat import).
  After pip install, these sys.path entries do not exist.

**Why it was hidden**:
  - All tests (Termux, CI, Colab) clone the repository and
    run from inside it.
  - SDK was never tested.
  - pip install . succeeded (wheel built) — the build
    step does not exercise imports.
  - The failure appears only when importing after install.

**Impact**: HIGH for SDK / packaging.
  - Blocks publishing on PyPI.
  - Blocks `pip install governance-kernel`.
  - Blocks any use outside the repository.
  - Does NOT affect V0.4-V0.7 (they run from repo).
  - Does NOT affect CI (runs from repo).
  - Does NOT affect Termux (runs from repo).

**Fix plan** (V0.7.16):

Option A — Refactor imports (cleanest):
  Change all 71 flat imports:
    BEFORE: import kill_switch
    AFTER:  from control import kill_switch
  Requires FREEZE_v0.7.16 (touches protected files).
  Time: 3-4 days.

Option B — Bootstrap sys.path in package __init__:
  Add governance_kernel/__init__.py that manipulates sys.path
  before submodules import.
  Time: 1-2 days. Hack, but works.

Option C — Wrapper package:
  Create governance_kernel/ with re-exports.
  Time: 2-3 days.

Recommended: Option A (cleanest for SDK).

**Cost estimate**: 3-4 days (Option A).

**Status**: PENDING. Documented only.

**Scientific note**: This is the 20th finding in the
J-0.8.x series. It reveals a class of problems invisible
until a specific mode is tested (import-after-install).
The lesson: testing "from inside the repo" is not the
same as testing "as an SDK".

## J-0.8.15 — J-0.8.2 absent from JOURNEY sequence

**Discovered**: 2026-09-23, extended review session
**Class**: Documentation gap
**Related**: J-0.8.1, J-0.8.3

**Symptom**:
  The J-0.8.x numbering sequence in docs/JOURNEY.md
  jumps from J-0.8.1 to J-0.8.3. No J-0.8.2 entry exists.

  Verification:
    grep "^## J-0.8" docs/JOURNEY.md
  Output:
    ## J-0.8.1
    ## J-0.8.3   <- no J-0.8.2
    ## J-0.8.4
    ...

  Additional verification:
    grep -rn "J-0.8.2\b" . --include="*.md"
  Only finds references to J-0.8.15 (this finding) and
  to J-0.8.20/21/28/29 (partial matches, not J-0.8.2).

    git log --all -S "J-0.8.2" -- docs/JOURNEY.md
  Finds no commit that ever added a J-0.8.2 entry.

**Root cause**:
  Unknown. The number was skipped when the J-0.8.x series
  was created (2026-09-22, during V0.7.5 to V0.7.9 fixes).
  Two possibilities:
    (a) J-0.8.1 and J-0.8.3 were written together, and the
        author simply skipped .2 by mistake.
    (b) A J-0.8.2 entry was drafted but never committed.
  No evidence supports either.

**Why it was hidden**:
  - JOURNEY.md does not assert sequence completeness.
  - No test checks for gaps.
  - The gap is small (one number) and easy to overlook.
  - Each later finding just used the next number without
    checking the previous one.

**Impact**: LOW.
  - No content is missing (no J-0.8.2 ever existed).
  - Only the numbering is discontinuous.
  - README and other docs reference J-0.8.1, J-0.8.3, etc.
    individually, not the count.
  - It was flagged as a finding (J-0.8.15) during review
    because the discontinuity was noticed.

**Resolution** (this commit):

  Documented as a numbering gap, not a missing finding.
  No content to restore.

  Decision: do NOT create a J-0.8.2 entry retroactively.
  Reason: numbers are historical; inventing .2 now would
  create false history. The gap is the record.

  HANDOVER.md already documents this in its J-0.8.x list:
    "(numbered 1, 3-11; J-0.8.2 is absent — see J-0.8.15)"

**Cost estimate**: 0 (verified, no fix required).

**Status**: CLOSED (2026-09-28).

**Scientific note**: This is the fourth finding (after
J-0.8.13, J-0.8.17, J-0.8.18) that closes as "verified,
no fix required". These are findings that turned out to
be documentation of a known state rather than actionable
defects. The pattern: review reveals small anomalies,
verification confirms they are benign, and closure is
the correct action. Not every finding requires a change.

## J-0.8.19 — HANDOVER claims 7 pending DOIs; only 3 exist

**Discovered**: 2026-09-23, extended review session
**Class**: Unverified claim
**Related**: HANDOVER (original)

**Symptom**:
  Original HANDOVER (pre-2026-09-23) claimed:
    "3 DOIs موجودة + 7 قيد الإنشاء = 10 قريباً"
    (3 DOIs exist + 7 pending = 10 soon)

  Verification in repository:
    grep -rohE "10\\.5281/zenodo\\.[0-9]+" . --include="*.md" | sort -u
  Result:
    10.5281/zenodo.22773364   (Concept DOI)
    10.5281/zenodo.22773365   (V0.5 DOI)
    10.5281/zenodo.22812967   (V0.6 DOI)
  Only 3 unique DOIs. No trace of 7 others.

**Root cause**:
  The "7 pending DOIs" was likely a plan for future
  releases (V0.7, V0.8, etc.), not a record of existing
  DOIs. The HANDOVER text conflated "planned" with
  "in progress".

**Why it was hidden**:
  - No test asserts DOI count.
  - The claim was plausible.
  - No one had audited DOIs against Zenodo.

**Impact**: LOW-MEDIUM.
  - For external credibility: 3 real DOIs (V0.5, V0.6,
    Concept) are visible.
  - The "7 pending" claim was aspirational, not factual.
  - HANDOVER rewrite (8eaccc9) removed the claim.

**Verification** (2026-09-28):

  Checked Zenodo directly via DOI URL:
    https://doi.org/10.5281/zenodo.22812967
  Result:
    - Published September 17, 2026
    - Version v0.6-closed
    - File: governance-kernel-v0.6-closed.zip (193.7 kB)
    - Author: Ahmed Ait Zaouit (Morocco)
  DOI is real and accessible.

  For the 3 DOIs:
    - 10.5281/zenodo.22773364 (Concept DOI)
    - 10.5281/zenodo.22773365 (V0.5)
    - 10.5281/zenodo.22812967 (V0.6)
  All visible in README.md and AUTHORS.md.

  The 7 claimed "pending" DOIs do not exist in the
  repository nor (presumably) on Zenodo.

**Resolution** (this commit):

  Documented as: 3 real DOIs, 0 trace of 7 others.
  No action needed.
  HANDOVER rewrite removed the misleading claim.

  Future: if DOIs are planned for V0.7, V0.8, etc.,
  list them explicitly with status (planned / pending /
  published), not as a count.

**Cost estimate**: 0 (verified, no fix required).

**Status**: CLOSED (2026-09-28).

**Scientific note**: This is the 5th finding (after
J-0.8.13, J-0.8.15, J-0.8.17, J-0.8.18) closing as
"verified, no fix required". The pattern: aspiration
written as fact. Lesson: distinguish "planned" from
"exists" in documentation.

## J-0.8.23 — Gate D not run since V0.2a

**Discovered**: 2026-09-23, extended review session
**Class**: Orphan test / no ongoing verification
**Related**: J-0.8.20 (Gate D layer 3), J-0.8.26 (V0.3 not in CI)

**Symptom**:
  tests/gate_d_benchmark.py exists (5,488 bytes,
  2026-09-13). docs/GATE_D_report.md exists (same date).

  But Gate D is NOT run by:
    - .github/workflows/test.yml   (no entry)
    - bootstrap.py                  (no entry)
    - tests/*/run_all.py            (no entry)

  Verification:
    grep -n "gate_d\|Gate D" .github/workflows/test.yml
    -> (empty)
    grep -n "gate_d\|Gate D" bootstrap.py
    -> (empty)
    grep -rn "gate_d" tests/*/run_all.py
    -> (empty)

  Last known run: 2026-09-13 (per GATE_D_report.md).

**Root cause**:
  Gate D predates the tests/gate_vN/ convention (V0.4+).
  It was created during V0.2a as a one-off benchmark.
  When V0.4 introduced gate suites with run_all.py and
  CI, Gate D was never integrated.

  Additionally: Gate D depends on the 'memory' branch
  being registered and 'memory_system' subject being
  present. On a fresh clone these are missing (until
  v0.7.14 added them via bootstrap).

**Why it was hidden**:
  - No test asserts that all tests/ files are exercised.
  - Gate D is in tests/ root, not in any gate_vN/ dir.
  - CI only runs V0.4, V0.5, V0.6, V0.7 (all in
    tests/gate_vN/).
  - The orphan status is invisible until someone
    actually tries to run Gate D.

**Impact**: MEDIUM.
  - A documented benchmark (GATE_D_report.md) claims
    results, but there is no way to reproduce them
    automatically.
  - Gate D would likely fail today because of
    J-0.8.20 (policy memory:write permission).
  - No CI catches regressions in the memory layer.

**Status**: CLOSED (2026-09-28) as documented orphan.

  Fix path (v0.7.17+):
    1. Fix J-0.8.20 (policy memory:write) first.
    2. Add step_run_gate_d() to bootstrap.py.
    3. Add a CI step: python tests/gate_d_benchmark.py.
    4. Optionally move to tests/gate_v02a/run_all.py.

  This entry records the current state. No code change
  in this commit.

**Cost estimate**: 0 (documented only).

**Scientific note**: This is the 6th finding in the
J-0.8.x series closing without code change. Together
with J-0.8.26 (V0.3 not in CI), it reveals a pattern:
test files written during V0.1-V0.3 were never integrated
into the automated suites that V0.4+ built. The V0.4+
convention (tests/gate_vN/ + run_all.py + CI) did not
retroactively capture earlier tests.

## J-0.8.22 — branch_manifest.yaml overstates memory contents

**Discovered**: 2026-09-23, extended review session
**Class**: Manifest vs reality mismatch
**Related**: J-0.8.20 (Gate D layer 3)

**Symptom**:
  memory/branch_manifest.yaml (version: "0.2.0",
  2026-09-13) declares 14 .py files across 5 categories:

    episodic:    event_log.py, event_index.py       (2)
    semantic:    node.py, edge.py, graph.py,
                 traversal.py                        (4)
    procedural:  trail.py, reinforcement.py,
                 decay.py                            (3)
    meta:        swarm.py, retriever.py,
                 consensus.py                        (3)
    dynamics:    weights.py, bounds.py              (2)

  Actual files in memory/:
    memory/__init__.py
    memory/gate.py
    memory/register_branch.py
    memory/episodic/__init__.py
    memory/episodic/event_log.py                    (1 of 2)
    memory/semantic/__init__.py
    memory/semantic/edge.py                         (1 of 4)
    memory/semantic/graph.py                        (2 of 4)
    memory/semantic/node.py                         (3 of 4)
    memory/semantic/traversal.py                    (4 of 4)

  Missing:
    episodic/event_index.py                         (1)
    procedural/  (entire directory)                 (3)
    meta/        (entire directory)                 (3)
    dynamics/    (entire directory)                 (2)
    -----
    Total missing: 9 files, 3 entire directories.

**Root cause**:
  The manifest was written during V0.2a (2026-09-13) as
  the intended memory layer architecture. Only the
  semantic layer and one episodic file were implemented.
  The procedural, meta, and dynamics sublayers were
  planned but never built.

  Version field still says "0.2.0" — it was never updated.

**Why it was hidden**:
  - memory/gate.py does not validate the manifest
    against actual files.
  - register_branch.py lists permissions, not files.
  - No test asserts manifest-vs-reality consistency.
  - The file is descriptive, not executable.

**Impact**: LOW-MEDIUM.
  - A reader of branch_manifest.yaml may believe the
    memory layer is fully implemented (it is not).
  - Does NOT affect V0.4-V0.7 (they don't rely on
    procedural/meta/dynamics).
  - Does NOT break Gate D (it uses semantic + episodic
    only).
  - The manifest is a V0.2a historical document.

**Resolution** (this commit):

  Documented as historical manifest, no fix planned.
  Decision: do NOT delete the planned file names.
  Reason: the manifest records V0.2a intent, and modifying
  it (to remove planned files) would erase the record of
  what was intended.

  memory/ is protected in G0.ZZ. Any change to
  branch_manifest.yaml requires FREEZE + exception.
  Given the LOW impact, this is not justified.

  Alternative considered: add a "status: planned"
  annotation to missing entries. Rejected for now —
  would need FREEZE and does not add much value.

**Cost estimate**: 0 (documented only).

**Status**: CLOSED (2026-09-28).

**Scientific note**: This is the 7th finding closing
without code change. The pattern is: a plan document
(manifest, README, HANDOVER) records intended state,
but the code evolves differently. The fix is not to
rewrite the document but to acknowledge it as a
snapshot of intent.

## J-0.8.25 — Two test files in repo root (V0.3 tests)

**Discovered**: 2026-09-23, extended review session
**Class**: File organization inconsistency
**Related**: J-0.8.26 (V0.3 not in CI), J-0.8.30 (README references)

**Symptom**:
  Two V0.3 test files exist in the repository root:

    tests_gate_v03_separation_smoke.py    (2,189 bytes)
    tests_gate_v03_six_combinations.py    (3,371 bytes)

  Meanwhile a directory tests/gate_v03/ also exists with
  five V0.3-era tests:

    tests/gate_v03/
    ├── g07_policy_separation.py
    ├── g09_repeatability_v2.py
    ├── g09_repeatability_v3.py
    ├── g09_statistical_repeatability.py
    └── g11_counterfactual.py

  So V0.3 tests are split across two locations:
  repository root (2 files) and tests/gate_v03/ (5 files).

**Root cause**:
  The V0.3 separation tests (separation_smoke,
  six_combinations) were written before the
  tests/gate_vN/ convention was established (in V0.4).
  They were placed at the repo root as standalone
  scripts. The tests/gate_v03/ directory contains a
  different set of V0.3-era tests (G0.7, G0.9, G0.11)
  that were organized differently.

  When V0.4 introduced tests/gate_v04/run_all.py, the
  root files were never moved. They remained as orphan
  scripts at the root, but still work when run from
  the repository root.

**Why it was hidden**:
  - Both root files work (run correctly from repo root).
  - They are not in any run_all.py.
  - No test asserts file layout.
  - The root-level naming (tests_gate_v03_*.py) looks
    intentional but is not part of any convention.

**Impact**: LOW.
  - Files work correctly (verified 2026-09-25 on Colab:
    six_combinations printed "6/6 combinations" and
    "ALL ASSERTIONS PASSED").
  - No impact on V0.4-V0.7.
  - The only issue is organization: they should be
    in tests/gate_v03/ for consistency.

**Status**: CLOSED (2026-09-28) as documented.

  Fix path (combined with J-0.8.26):
    1. Move both files to tests/gate_v03/.
    2. Adjust sys.path lines:
       BEFORE: sys.path.insert(0, 'kernel')
       AFTER:  sys.path.insert(0, '../../kernel')
       (or use Path(__file__).resolve() approach)
    3. Create tests/gate_v03/run_all.py that runs all
       7 files (5 existing + 2 moved).
    4. Add a CI step for V0.3.

  This entry records the current state. No code change
  in this commit. The fix is scheduled together with
  J-0.8.26 (V0.3 not in CI), since they are the same
  reorganization.

**Cost estimate**: 0 (documented only). Combined fix
estimate: 2-3 hours.

**Scientific note**: This is the 8th finding closing
without code change. Together with J-0.8.23 (Gate D
orphan) and J-0.8.26 (V0.3 not in CI), it reveals a
consistent pattern: tests written before V0.4 are not
integrated into the V0.4+ convention
(tests/gate_vN/run_all.py + CI). The fix is a single
reorganization that addresses all three.

## J-0.8.33 — GATES_v0.3_G07_report.md drift kappa inaccuracy

**Discovered**: 2026-09-28, while investigating J-0.8.26
**Class**: Documentation inaccuracy
**Related**: J-0.8.26 (V0.3 not in CI)

**Symptom**:
  docs/GATES_v0.3_G07_report.md (2026-09-14) states:

    ### Scenario: drift (non-trivial)
    - Policy effect | C: 1.000 ± 0.000
    - Policy effect | D: 0.966 ± 0.011
    - |Δκ| = 0.034 → HOLDS

  But running the same test (tests/gate_v03/g07_policy_separation.py)
  on 2026-09-28 gives:

    drift: |kappa_C - kappa_D| = 0.287  -> MAY FAIL

  Discrepancy: 8.4x (0.034 vs 0.287).

  For noise, both agree:
    Report: |Δκ| = 0.044 -> HOLDS
    Now:    |kappa_C - kappa_D| = 0.044 -> HOLDS

  For fixed, both agree:
    Report: |Δκ| = 0.300 -> MAY FAIL
    Now:    |kappa_C - kappa_D| = 0.300 -> MAY FAIL

  So the discrepancy is specific to the drift scenario.

**Verification** (2026-09-28):

  1. Determinism: ran g07 three times consecutively.
     All three gave identical numbers (0.300 / 0.287 / 0.044).
     Code is deterministic.

  2. Environment portability:
     - environment.py uses random.Random(seed)
       -> deterministic Mersenne Twister, same across
          Python versions and platforms.
     - Uses math.sin for drift signal -> IEEE 754, stable.
     - No os.environ, no platform-dependent calls,
       no global random.

  3. seed variation:
     Changed seed from 1000+r to r (temporary edit, then
     git checkout restored).
     drift: 0.276 (still > 0.2). Not 0.034.
     So different seed does not explain the report value.

  4. Git history:
     tests/gate_v03/g07_policy_separation.py  -> last modified
       2026-09-14 (dcf170e).
     kernel/separation/environment.py        -> last modified
       2026-09-14 (dcf170e).
     No commits between then and now.

**Root cause**:
  Most likely: typo in the report (0.034 written instead
  of 0.287 or 0.276). The other two scenarios (fixed,
  noise) match exactly, which rules out an environmental
  or code-based explanation.

  Less likely but possible: the report was generated from
  a draft version of the test that was not the one
  committed as dcf170e.

**Why it was hidden**:
  - Report stated "SEPARATION HOLDS" for drift, which is
    plausible at a glance.
  - "2/3 gates" in V0.3_SUMMARY.md was accepted as-is.
  - No one re-ran V0.3 after 2026-09-14.
  - J-0.8.26 (V0.3 not in CI) meant V0.3 was never
    automatically re-verified.

**Impact**: LOW.
  - V0.3 conclusion ("2/3 gates") is unchanged.
  - G0.7 verdict for drift is MAY FAIL, not HOLDS.
  - This slightly changes the interpretation: in the
    drift scenario, Policy is NOT fully architecture-
    independent.
  - Does NOT affect V0.4-V0.7.
  - Does NOT affect kernel.

**Resolution** (this commit):

  Documented. No fix in this commit.
  The report is a historical document.

  Future: if V0.3 documentation is revised, update the
  drift line in GATES_v0.3_G07_report.md to state the
  actual value (0.287). This would require editing a
  doc under docs/, which is not protected but is
  preferred to be done in a dedicated pass.

**Cost estimate**: 0 (documented only).

**Scientific note**: This is the 9th finding closing
without code change. It reveals the value of J-0.8.26:
because V0.3 was never in CI, its reported numbers were
never re-verified. The discovery of this inaccuracy
was only possible by manually re-running the test.

## J-0.8.27 — V0.7 timing 4.65s without baseline

**Discovered**: 2026-09-23, extended review session
**Class**: Performance observation
**Related**: ADDENDUM_2026-09-23

**Symptom**:
  HANDOVER_ADDENDUM_2026-09-23 recorded:
    V0.7 | 19/19 | 4.65s (Colab, 2026-09-23)

  No Termux baseline was recorded at that time.
  The value was Colab-specific.

**Root cause**:
  Timing varies significantly across environments:
    - Colab: cloud x86_64, 4 CPU cores, 13 GB RAM
    - Termux: phone ARM, throttled CPU, limited RAM
  A single "4.65s" was misleading without environment
  context.

**Why it was hidden**:
  - The value appeared in a table titled "Colab".
  - But it was also cited without environment in
    Section 3.2 of the same addendum.
  - No Termux baseline existed.

**Impact**: LOW.
  - No user-facing claim depended on it.
  - It is a performance observation, not a defect.

**Verification** (2026-09-28):

  Both environments measured with 3 runs each:

  Colab:
    V0.4: 0.77s (min 0.75, max 0.78)
    V0.5: 0.81s (min 0.79, max 0.84)
    V0.6: 2.55s (min 2.23, max 3.20)
    V0.7: 6.31s (min 5.46, max 7.12)
    bootstrap: 0.50s (min 0.28, max 0.89)

  Termux (Android, ARM):
    V0.4: 8.64s (min 8.62, max 8.66)
    V0.7: 42.46s (min 42.00, max 43.14)

  Comparison:
    V0.4: Colab is ~11.2x faster than Termux
    V0.7: Colab is ~6.7x faster than Termux

  Colab value changed from 4.65s (2026-09-23) to 6.31s
  (2026-09-28). Likely due to CPU throttling — the
  current run showed 5.46s to 7.12s range.

**Resolution** (this commit):

  Documented. Full baseline now available for both
  environments. J-0.8.27 is closed as "resolved:
  baseline complete".

  Future measurements should always include the
  environment label.

**Cost estimate**: 0 (observation).

**Status**: CLOSED (2026-09-28).

**Scientific note**: This is the 10th finding closing
without code change. It highlights the importance of
environment context for performance numbers. A single
timing value is meaningless without stating the
hardware and Python version.

**Performance summary** (for reference):

  Environment:       Colab           Termux         Ratio
  V0.4:              0.77s           8.64s          ~11.2x
  V0.5:              0.81s           (not measured) -
  V0.6:              2.55s           (not measured) -
  V0.7:              6.31s           42.46s         ~6.7x
  bootstrap:         0.50s           ~0.5s          ~1x

## J-0.8.37 — No standard benchmark for governance kernels

**Discovered**: 2026-09-28, during testing session on Colab
**Class**: Market positioning / Category definition
**Related**: J-0.8.36 (planned comparison), SDK roadmap

**Symptom**:
  Attempted to compare Governance Kernel against standard
  open-source governance/policy tools. Found no comparable
  category.

  Tools examined (2026-09-28):
    - OPA (Open Policy Agent, CNCF)         v1.21.0
      Category: general policy engine (Rego).
      Interface: opa eval -d policy.rego -i input.json
      Scope: allow/deny decisions on JSON input.
      Not agent-aware. No trust ladder. No audit chain.
      No kill switch. Policy only.

    - Guardrails AI                          v0.11.0
      Category: LLM output validation.
      Interface: Guard(prompt, validator).validate(output)
      Scope: checks LLM outputs against validators.
      Not agent-aware. No action governance.

    - NeMo Guardrails (NVIDIA)               v0.24.1
      Category: LLM dialogue safety.
      Interface: RailsConfig.from_path() + dialog flow.
      Scope: filters LLM conversations (prompt injection,
      content moderation).
      Not agent-aware. No permission model.

    - Cedar (AWS)
      Category: policy language (Rust).
      Interface: cedar-policy CLI / crate.
      Scope: policy evaluation, formal verification.
      Not available as a pip-installable Python package
      for easy comparison.

  Conclusion: no benchmark or competing tool addresses
  the same scope as Governance Kernel:
    - governance of AGENT ACTIONS (not LLM outputs)
    - trust ladder per subject
    - audit hash-chained log
    - kill switch
    - resource governor
    - multi-agent consensus + delegation

**Root cause**:
  AI Safety tooling evolved along two dominant axes:
    (a) LLM-centric (NeMo, Guardrails AI, HarmBench).
    (b) General policy engines (OPA, Cedar).

  Neither addresses "governance kernel for agents" as a
  formal category.

  This is both:
    - an opportunity (no direct competitor), and
    - a challenge (no established benchmark to measure
      against).

**Why it was hidden**:
  - Assumed direct comparison was possible.
  - Discovered only when attempting the comparison.

**Impact**: MEDIUM (positive).
  - Clarifies that the project occupies a niche.
  - Also clarifies that no external benchmark validates
    the claim.
  - Justifies building a dedicated benchmark as future
    work.

**Resolution** (this commit):

  Documented. No fix in this commit.

  Decision: do NOT attempt further direct comparison
  with OPA / NeMo / Guardrails AI / Cedar.
  Reason: scope mismatch is fundamental, not superficial.

  Future work (V0.8+):
    - Define a "Governance Kernel Benchmark" specification.
    - Include agent-action scenarios (subject, action,
      expected decision, rationale).
    - Publish openly (GitHub + arXiv).
    - Invite external contributors.

**Cost estimate**: 0 (documented only).

**Scientific note**: This is the 11th finding closing
without code change. It is also the first finding that
is PURELY about positioning, not about an internal
defect. It documents a gap in the AI Safety tooling
landscape: LLM-centric safety (NeMo, Guardrails AI)
and general policy engines (OPA, Cedar) exist, but
agent-action governance does not have a standard
benchmark.

**Related observation**:
  Even if direct comparison is impossible, indirect
  comparison is possible:
    - Kernel's policy engine can be translated to Rego
      for OPA (policy-only comparison).
    - Kernel's decision engine can be described as
      "governance for agents" and positioned ABOVE
      OPA/Cedar, not as a replacement.

  This positions the project as a layer that could
  use OPA/Cedar internally, not compete with them.

## J-0.8.34 — V0.3_SUMMARY says 2/3 gates; actual 1/5

**Discovered**: 2026-09-28, during V0.3 investigation
**Class**: Documentation inaccuracy
**Related**: J-0.8.33 (G07 report), J-0.8.35, J-0.8.36

**Symptom**:
  docs/V0.3_SUMMARY.md states:
    "الحالة: مكتمل تقنياً (2/3 gates CLOSED, 1 finding documented)"

  In reality, running tests/gate_v03/run_all.py on
  2026-09-28 gives:
    G0.7 Policy Separation           FAILED (drift 0.287)
    G0.9 Statistical Repeatability   FAILED (noise)
    G0.9 v2 Repeatability (std)      FAILED (D architecture)
    G0.9 v3 Same-seed Repeatability  CLOSED
    G0.11 Counterfactual             FAILED (drift)
    --> V0.3 gates: 1/5 closed

  Discrepancy: 2/3 (documented) vs 1/5 (actual).

**Root cause**:
  V0.3 was documented in 2026-09-14 as "2/3 gates".
  The claim "2/3" may have referred to:
    - G0.7 (HOLDS in noise, MAY FAIL in drift)
    - G0.9 (CLOSED, though the threshold was unrealistic)
    - G0.11 (FAILED as documented)
  Counting only the "successes" gives 2/3. But the
  actual test count (5 tests) yields 1/5 when all
  failures are honest.

  The phrase "1 finding documented" (G0.11) implies
  only one failure. Actually there are 4 failures.

**Why it was hidden**:
  - V0.3 was never in CI (J-0.8.26).
  - Reports were accepted as-is (J-0.8.33 pattern).
  - The phrase "2/3" was plausible.
  - No one re-ran the tests until 2026-09-28.

**Impact**: LOW-MEDIUM (documentation only).
  - Does NOT affect V0.4-V0.7.
  - Does NOT affect kernel.
  - V0.3 is a research finding, not a production gate.
  - The lesson is methodological: reports without
    continuous verification drift from reality.

**Resolution** (this commit):

  Documented. No fix.
  Decision: do NOT rewrite V0.3_SUMMARY.md now
  (would require a dedicated pass through V0.3
  documentation).
  Future work: when V0.3 is revised, replace "2/3"
  with the accurate "1/5 (4 tests failing in drift/noise;
  see J-0.8.33/35/36)".

**Cost estimate**: 0 (documented only).

**Status**: CLOSED (2026-09-29).

**Scientific note**: This is the 12th finding closing
without code change. It is directly related to J-0.8.33
(G07 drift kappa inaccuracy) and J-0.8.26 (V0.3 not in
CI). The three together show a pattern: without CI,
reported numbers can drift from reality.

## J-0.8.35 — G0.9 statistical threshold unrealistic in noise

**Discovered**: 2026-09-28, during V0.3 investigation
**Class**: Test design (threshold scope)
**Related**: J-0.8.34

**Symptom**:
  tests/gate_v03/g09_statistical_repeatability.py
  checks "agreement >= 0.90" for all scenarios,
  including "noise".

  In the noise scenario, Environment._signal() returns
  random.gauss(0, 0.5) — pure Gaussian noise. There is
  no signal to agree on. Each run draws a new sequence.

  Actual results (2026-09-28):
    noise: C-S 0.42, C-A 0.42, D-S 0.50, D-A 0.50
    (all FAIL vs threshold 0.90)

  This is not a defect in the kernel. It is a mismatch
  between the test's expected behavior and the actual
  randomness of the noise scenario.

**Root cause**:
  The threshold (0.90) was chosen for the drift
  scenario (sinusoidal, deterministic). It was
  applied indiscriminately to noise (random).

  The test does not distinguish:
    - deterministic signals (fixed, drift)
    - random signals (noise)

  For a random signal, the maximum agreement is
  ~50% (coin-flip). A threshold of 0.90 is unreachable.

**Why it was hidden**:
  - V0.3 was run once (2026-09-14).
  - The report may have excluded noise from the pass
    criteria.
  - No CI, no continuous verification.
  - Same pattern as J-0.8.33/34.

**Impact**: LOW.
  - V0.3 result "1/5" counts G0.9 statistical as FAILED
    (J-0.8.34).
  - The FAILURE itself is a design issue, not a defect
    in the kernel.
  - Fix would be: either exclude noise from the G0.9
    statistical test, or relax the threshold for
    noise.

**Status**: CLOSED (2026-09-29) as documented.

  Decision: do NOT modify the test now (would need
  a dedicated pass through V0.3 tests + FREEZE if
  the file is protected; it is not, but consistency
  matters).
  Documented as part of the V0.3 report inaccuracy
  series.

**Cost estimate**: 0 (documented only).

**Scientific note**: This finding reveals that
thresholds are scenario-specific. The same threshold
(0.90) that makes sense for a deterministic signal
(drift) is meaningless for a random signal (noise).
A well-designed benchmark should declare thresholds
per scenario.

## J-0.8.36 — G0.9 v2 threshold unrealistic for D architecture

**Discovered**: 2026-09-28, during V0.3 investigation
**Class**: Test design (threshold scope)
**Related**: J-0.8.34, J-0.8.35

**Symptom**:
  tests/gate_v03/g09_repeatability_v2.py checks
  "std(final_state) <= 0.30" for all architectures,
  including Distributed (D).

  D is inherently stochastic: it depends on local
  observations that vary per node.

  Actual results (2026-09-28, fixed + drift):
    C-S: 0.0000 [PASS]
    C-A: 0.0000 [PASS]
    D-S: 0.7762 [FAIL]
    D-A: 0.6565 [FAIL]

  C (Central) is deterministic (std = 0.0000).
  D (Distributed) is stochastic (std ~ 0.7).

  Both are correct per their design. The threshold
  (0.30) is appropriate for C but not for D.

**Root cause**:
  The threshold was likely chosen for C (deterministic).
  Applied to D (stochastic), it fails systematically.

  The test does not distinguish:
    - deterministic architectures (C)
    - stochastic architectures (D)

**Why it was hidden**:
  - Same pattern as J-0.8.33/34/35.
  - No CI.
  - Accepted as-is for ~14 days.

**Impact**: LOW.
  - V0.3 "1/5" counts G0.9 v2 as FAILED (J-0.8.34).
  - The FAILURE is a design issue, not a defect
    in the kernel.
  - Fix would be: use different thresholds per
    architecture (C: 0.01, D: 0.80).

**Status**: CLOSED (2026-09-29) as documented.

  Decision: do NOT modify the test now.
  Documented as part of the V0.3 report inaccuracy
  series.

**Cost estimate**: 0 (documented only).

**Scientific note**: This is the third finding in
the J-0.8.33-36 cluster — all reveal the same
pattern: "thresholds and expectations from one
scenario, applied blindly to another." The lesson:
design each test with its own scenario-specific
thresholds. Generalizing thresholds across
heterogeneous scenarios produces misleading FAILs
or misleading PASSes.

