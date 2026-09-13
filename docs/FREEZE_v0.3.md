# FREEZE_v0.3 — تجميد معاملات فصل Architecture ⊥ Policy + 3 وكلاء

التاريخ: 2026-09-13
الإصدار: V0.3
الحالة: مجمّد قبل التنفيذ
المراجع: CHARTER.md, GATES.md, V0.3_SCOPE_LOCK.md
المرجع النظري: Related_Work_Novelty_Audit (من AZ-FSF)

## 1. الغاية

V0.3 يثبت أن نواة الحكم V0.1 تحكم وكلاء حقيقيين، لا محاكاة.
شرط النجاح: وكيل لا يستطيع تجاوز البوابة، حتى لو حاول.

## 2. النطاق (مقفل بـ SCOPE_LOCK)

داخل النطاق:
- فصل Architecture (InfoModel) عن Policy (DecisionPolicy)
- 3 وكلاء deterministic (بدون LLM)
- Gate 0 الجديدة (G0.7, G0.9, G0.11)

خارج النطاق (صريح):
- لا V0.2b/c/d
- لا LLM
- لا واجهة ويب
- لا تشفير إضافي

## 3. البنية الملفية

kernel/separation/
  info_model.py         (واجهة Architecture)
  central_info.py       (مركزي)
  hierarchical_info.py  (هرمي)
  distributed_info.py   (موزع)
  decision_policy.py    (واجهة Policy)
  simple_policy.py      (قرار ثابت)
  adaptive_policy.py    (قرار متكيف)

agents/
  base_agent.py
  file_agent.py
  compute_agent.py
  query_agent.py
  register_agents.py    (تسجيل 3 وكلاء بتوقيع المالك)

tests/
  gate_v03/
    g07_policy_separation.py
    g09_statistical_repeatability.py
    g11_counterfactual_info.py

## 4. المعاملات المجمّدة

### 4.1 الوكلاء الثلاثة
MAX_AGENTS = 3
AGENT_NAMES = ["FileAgent", "ComputeAgent", "QueryAgent"]
AGENT_TRUST_DEFAULT = 0.7
AGENT_ROLE_DEFAULT = "agent_high"

### 4.2 صلاحيات كل وكيل (من policy/policies/default.yaml)
FileAgent:
  - tool:file_read
  - memory:read

ComputeAgent:
  - tool:python
  - memory:read

QueryAgent:
  - memory:read
  - memory:graph_traverse

ملاحظة: لا وكيل يملك tool:file_write في V0.3.

### 4.3 Architecture ⊥ Policy — التعريف المُلزم
Architecture = InfoModel.gather()  (من أين تأتي المعلومة)
Policy = DecisionPolicy.decide()    (كيف تُعالج المعلومة)
القاعدة: Node لا تعرف نوعها. تستقبل كائنين فقط.

### 4.4 ميزانية الاختبار
RUNS_PER_TEST = 10
OPS_PER_RUN = 50
TOTAL_OPS = 500
THREADS = 1  (لا توازي)

### 4.5 حدود القبول
policy_separation_kappa_min = 0.8
statistical_cv_max = 0.05
counterfactual_corr_max = 0.3

## 5. Gate 0 الجديدة — التعريفات

### G0.7 Policy Separation
السؤال: هل يمكن تغيير Architecture دون تغيير Policy، والعكس؟
الاختبار: شغّل 4 تركيبات (C-S, C-A, D-S, D-A) على نفس المشكلة.
القياس: Cohen's Kappa بين نتائج كل زوج متقابل.
النجاح: kappa >= 0.8.
الفشل: kappa < 0.8 (يعني الطبقات متشابكة).

### G0.9 Statistical Repeatability
السؤال: هل النتيجة ثابتة عبر 10 تشغيلات؟
الاختبار: شغّل 10 مرات بنفس (seed, config).
القياس: CV = std / mean (Coefficient of Variation).
النجاح: CV <= 0.05 (5%).
الفشل: CV > 0.05.

### G0.11 Counterfactual Information Test
السؤال: هل الفرق في الأداء سببه الوصول للمعلومات فقط؟
الاختبار: غيّر Architecture فقط، أبق كل شيء آخر ثابتاً.
القياس: correlation بين (فرق المعلومات) و(فرق الأداء).
النجاح: corr <= 0.3 (فرق ضعيف، يعني الأداء لا يفسره إلا المعلومات).
الفشل: corr > 0.3 (هناك عوامل مخفية).

## 6. معايير النجاح النهائية (Pre-registered)

| المعيار | العتبة | القياس |
|---------|--------|--------|
| 3 وكلاء يعملون | 3/3 | end-to-end test |
| بوابة تحكم الوكلاء | 100% | كل عملية تمر عبر governed_action |
| G0.7 | kappa >= 0.8 | الاختبار الرسمي |
| G0.9 | CV <= 0.05 | الاختبار الرسمي |
| G0.11 | corr <= 0.3 | الاختبار الرسمي |
| لا انحدار | 0 أخطاء | 17 اختبار V0.1/V0.2 يبقى ناجحاً |

## 7. معايير الفشل (Pre-registered)

| السيناريو | الحكم |
|-----------|-------|
| 3/3 وكلاء + كل Gates نجحت | نجاح كامل — ننتقل لـ V0.4 |
| 3/3 وكلاء + 1-2 Gates فشلت | نجاح جزئي — تصحيح قبل V0.4 |
| 2/3 وكلاء أو أقل | فشل — مراجعة التصميم |
| انحدار في V0.1/V0.2 | فشل كامل — إصلاح فوري |

## 8. Threats to Validity (مُعلنة)

### Construct Validity
- هل "الوكيل الحقيقي" يُقاس فعلاً؟ 3 وكلاء deterministic قد لا يمثلون "الحقيقي".
- هل 4 تركيبات A×P كافية لاختبار الفصل؟

### Internal Validity
- قد يكون هناك coupling مخفي في الكود، لا يكشفه kappa.
- الكتابة الذاتية للاختبارات = circular validation.

### External Validity
- 3 وكلاء على هاتف قد لا يتعمم على 300 وكيل على خادم.
- النتائج مع deterministic قد لا تتعمم مع LLM.

### Statistical Conclusion Validity
- 10 تكرارات × 50 عملية = 500 نقطة. كافية؟
- Power Analysis قبل التشغيل النهائي.

## 9. ما لن نفعله بعد رؤية النتائج

- لن نغيّر العتبات (kappa, CV, corr).
- لن نضيف اختباراً لتحسين النسبة.
- لن نُخفي أي نتيجة سلبية.
- لن نُعدّل FREEZE بعد اليوم.

## 10. المراجع

- docs/V0.3_SCOPE_LOCK.md — ما لن نفعله
- docs/V0.3_NOVELTY_AUDIT_DRAFT.md — ما يميزنا فعلاً
- docs/V0.4_PREREGISTRATION_DRAFT.md — قالب المرحلة القادمة
- docs/CLAIM_LEVELS.md — تصنيف ادعاءاتنا

## 11. التوقيع

هذا الملف مجمّد بتاريخ 2026-09-13.
أي تعديل يحتاج FREEZE_v0.3_rev1.md + تسجيل السبب.

الحالة: FROZEN
الإصدار: v0.3.0
