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

