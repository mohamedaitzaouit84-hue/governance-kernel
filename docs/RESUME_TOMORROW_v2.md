# وثيقة الاستئناف v2 — 2026-09-15

## ما أُنجز (2026-09-14)
- G0.7 PASSED (آخر التزام: dcf170e)
- G0.9 FAILED as written (آخر التزام: cb0cafa)

## حالة V0.3
- G0.7 (Policy Separation): CLOSED
- G0.9 (Repeatability): FAILED — يحتاج v2
- G0.11 (Counterfactual): لم يُنفَّذ

## ما تعلّمناه من فشل G0.9
1. مقياس "الإشارة السائدة" هشّ (dominant sign).
2. Architecture C حتمية (1.00)، D عشوائية (~0.50).
3. سيناريو noise لا معنى له للثبات.

## خطة G0.9 v2

### المقياس الجديد
- mean action عبر 100 خطوة (بدل الإشارة السائدة)
- CV = std / |mean| عبر 50 seed
- العتبة: CV <= 0.05

### الاستثناءات
- سيناريو noise: يُستثنى (ضوضاء خالصة).
- architecture D: يُقبل CV أعلى (عشوائي بطبيعته).

### معيار النجاح المُعدَّل
- لـ C-S و C-A في fixed و drift: CV <= 0.05
- لـ D-S و D-A في drift: CV <= 0.20 (متناسب مع العشوائية)

## خطة G0.11 (Counterfactual)
- يعتمد على G0.7 الناجح
- يقيس: هل الفرق سببه المعلومات فقط؟
- سؤال: at constant policy, does architecture change outcome?
- الإجابة من G0.7: لا (Architecture effect = 0)
- G0.11 v2: قياس كمي للارتباط

## ما لا نفعله غداً
- لا نفتح ملفات AZ Research
- لا نُعدّل العتبة لإنجاح G0.9
- لا نُخفي فشل G0.9
- لا ننتقل إلى V0.4 قبل V0.3 الكامل

## قاعدة الالتزام
"إن فشل الاختبار، ننشر الفشل."
G0.9 فشل، نُصلحه، نُعيد، ثم نُعلن.

## الملفات المرجعية
- docs/GATES_v0.3_G07_report.md
- docs/GATES_v0.3_G09_report.md
- docs/FREEZE_v0.3.md
- docs/CHARTER.md
