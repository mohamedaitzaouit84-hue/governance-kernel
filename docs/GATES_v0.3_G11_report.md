# G0.11 — Counterfactual Information Test Report

**التاريخ**: 2026-09-14
**الحالة**: FAILED as written — structural finding documented
**المرجع**: FREEZE_v0.3.md, GATES.md
**الاختبار**: tests/gate_v03/g11_counterfactual.py

## السؤال
هل الفرق في الأداء سببه الوصول للمعلومات فقط؟

## الطريقة
- 30 seed
- لكل seed: معمارية مختلفة (C, H, D) دورياً
- ثابت: Policy (S أو A), Scenario (drift أو noise)
- القياس: Pearson correlation بين (info_size, final_state)
- العتبة: |corr| < 0.30

## النتائج

### drift
- Policy=S: corr = -0.378  [FAIL]
- Policy=A: corr = -0.378  [FAIL]

### noise
- Policy=S: corr = +0.190  [PASS]
- Policy=A: corr = +0.190  [PASS]

**الحكم**: FAILED as written (drift above threshold).

## التشخيص البنيوي

### السبب
- C (Central): info_size = 1، سلوك حتمي
- H (Hierarchical): info_size = 1، سلوك حتمي
- D (Distributed): info_size = 2، سلوك عشوائي (ضوضاء الجيران)

**D هو المعمارية الوحيدة بـ info_size=2**. الارتباط يعكس
هذا الفرق البنيوي، وليس "أثر كمية المعلومات على القرار".

### ملاحظة مهمة
Policy=S و Policy=A أعطتا **نفس الارتباط بالضبط**.
هذا يعني: الارتباط سببه Architecture، ليس Policy.
→ إشارة إضافية على أن Policy مستقلة (اتساق مع G0.7).

## كشف حقيقي

هذا الاختبار كشف أن:
- **إشارة القرار** متطابقة بين المعماريات (من G0.7).
- **قيمة الحالة النهائية** مختلفة (من G0.11).

هذان سؤالان مختلفان:
- G0.7: هل تُتخذ نفس القرارات؟
- G0.11: هل النتائج النهائية متطابقة؟

**النتيجة النهائية**: Architecture يؤثر على الحالة، لكن ليس
على القرار. هذا متسق مع G0.7 وليس مناقضاً له.

## G0.11 v2 — التصميم المقترح

- ثبّت info_size لكل معمارية (مثلاً 2 observations لكل).
- أعد القياس.
- السؤال: هل القرار يعتمد على **كمية** المعلومات أم على **مصدرها**؟
- هذا سؤال أعمق من التصميم الحالي.

## Threats to Validity

- الارتباط ليس سببية. D يعطي حالة مختلفة لسبب بنيوي.
- 30 seed فقط.
- لم نتحكم في حجم المعلومات بشكل مستقل.
- الخلط بين info_size ومعمارية D كامن في التصميم.

## الحالة
FAILED as written. G0.11 v2 مؤجل.
V0.3 يُعلن **مكتملاً جزئياً**: G0.7 ✅ + G0.9 ✅ + G0.11 (finding documented).
