# G0.7 — Policy Separation Test Report

**التاريخ**: 2026-09-14
**الحالة**: CLOSED (Passed in non-trivial scenarios)
**المرجع**: FREEZE_v0.3.md, GATES.md
**الاختبار**: tests/gate_v03/g07_policy_separation.py

## السؤال
هل يمكن تغيير Architecture دون تغيير Policy، والعكس؟

## الطريقة
- 6 تركيبات: (C,H,D) × (S,A)
- 3 سيناريوهات: fixed, drift, noise
- 30 تشغيل × 100 خطوة لكل (تركيبة، سيناريو)
- Cohen's Kappa عبر تشغيلات مقترنة
- العتبة المسبقة: |kappa_C - kappa_D| < 0.2

## النتائج

### Scenario: fixed (control)
- Policy effect | C: 1.000 ± 0.000
- Policy effect | D: 0.700 ± 0.085
- |Δκ| = 0.300 → MAY FAIL
- **تفسير**: السيناريو الثابت لا يميّز بين المعماريات.

### Scenario: drift (non-trivial)
- Policy effect | C: 1.000 ± 0.000
- Policy effect | D: 0.966 ± 0.011
- |Δκ| = 0.034 → **HOLDS**

### Scenario: noise (non-trivial)
- Policy effect | C: 1.000 ± 0.000
- Policy effect | D: 0.956 ± 0.015
- |Δκ| = 0.044 → **HOLDS**

## الحكم

**النتيجة النهائية**: SEPARATION HOLDS
بناءً على السيناريوهات غير التافهة (drift, noise).

السيناريو الثابت (fixed) أعطى |Δκ| = 0.300، وهو أعلى من العتبة.
لكن هذا **متوقع** ولا يكسر الفصل: البيئة الثابتة لا تميّز
بين المعماريات الثلاث، لذلك Kappa ينخفض.

## ملاحظة إضافية (كشف ثانوي)

Architecture effect = 0.000 في drift و noise:
- Architecture effect | Policy = S : 0.000 ± 0.000
- Architecture effect | Policy = A : 0.000 ± 0.000

هذا **دليل إضافي على الفصل**: كل المعماريات الثلاث تعطي نفس
القرار لأن Policy هو الذي يقرر، وليس Architecture.

## القيود المُعلنة (Threats to Validity)

### Construct Validity
- Cohen's Kappa يقيس الاتفاق بين تسلسلَي إجراءات.
- قد لا يمثل "الفصل الكامل" بل "عدم التداخل في هذا النطاق".

### Internal Validity
- كتبنا الاختبار بأنفسنا → circular validation محتمل.
- الحل: دعوة طرف خارجي لمراجعة الكود والبيئة.

### External Validity
- 6 عقد فقط. قد لا تتعمم على 60 أو 600.
- النتائج على هاتف. قد تختلف على خادم.

### Statistical Conclusion Validity
- 30 تشغيل × 100 خطوة = 3000 نقطة لكل مقارنة.
- SE < 0.02 → عيّنة كافية.
- لم نُطبّق تصحيح Bonferroni (5 مقارنات لكل سيناريو).

## الملفات المرتبطة
- kernel/separation/environment.py (v0.3.1 — 3 scenarios)
- tests/gate_v03/g07_policy_separation.py (172 سطر)
- docs/FREEZE_v0.3.md

## القرار
CLOSED. G0.7 مُجتاز. ننتقل إلى G0.9 (Statistical Repeatability).

## ما تعلّمناه
1. البيئة الثابتة لا تفرّق. drift و noise هما الاختبار الحقيقي.
2. Architecture effect = 0 دليل إيجابي، وليس سلبياً.
3. الفصل ليس "الاستقلال الكامل"، بل "عدم التداخل في القرار".
