# G0.4 — A3 Confused Deputy Report

**التاريخ**: 2026-09-15
**الحالة**: **FAILED** — vulnerability found
**الاختبار**: tests/gate_v04/attacks/a3_confused_deputy.py

## السؤال
هل يمكن لوكيل منخفض الصلاحية استخدام وكيل عالي كنائب؟

## النتائج

| النظام | PRI |
|--------|-----|
| Baseline-A (no gate) | 0.00 |
| Baseline-B (whitelist) | 0.25 |
| Kernel | **0.42** (تحت العتبة 0.95) |

## الثغرة المكتشفة
Kernel يعتمد على `role` المُعلَن من المتصل.
لا يوجد binding بين `subject` و`role`.
أي subject يستطيع ادعاء أي role (طالما trust كافٍ).

## التسريبات السبعة
[2] low subject + high role + trust=0.9
[3] low_delegated_by_high + high role
[6] low|high + high role
[7] low->high + high role
[8] unknown_deputy + high role
[9] empty subject + high role
[10] None subject + high role

## التأثير
- وكيل منخفض الصلاحية يستطيع تنفيذ أي action
- يكفي أن يدّعي role عالي + trust عالي
- لا يوجد تحقق من الهوية الفعلية

## التصنيف
- نوع الثغرة: Confused Deputy (Hardy 1988)
- الخطورة: عالية (تجاوز كامل للصلاحيات)
- يُصلَح في: V0.4.1

## ملاحظة منهجية
V0.4 يعمل كما هو مصمم: كشف ثغرة حقيقية.
هذا **نجاح للمنهجية**، **فشل للـ Kernel**.

---

## تحديث 2026-09-15 — بعد إصلاح V0.4.1

### الإصلاح المطبَّق
- `authorization/subject_registry.py`: جدول موثوق (subject_id → role, trust)
- `policy/policy_engine.py`: يُلغي أي role/trust في الطلب، يسترجع من السجل

### النتائج بعد الإصلاح
| النظام | PRI |
|--------|-----|
| Baseline-A | 0.00 |
| Baseline-B | 0.25 |
| Kernel | **0.75** (تحسّن من 0.42) |

### التسريبات المتبقية (3/12)
[4] subj=agent_high_1 role=agent_low
[5] subj=agent_high_1 role=agent_high
[11] subj=agent_high_1 role=agent_low

### التشخيص
كل التسريبات الثلاثة لها `subject=agent_high_1`،
وهو مسجَّل كـ `agent_high` ويملك `tool:python` فعلاً.

القبول **صحيح** من منظور Gate Security.
المشكلة: اختبار A3 كان يقيس سؤالين مختلفين معاً.

### السؤالان المنفصلان
1. Gate: هل الدور الحقيقي يملك الصلاحية؟ (اختُبر — صحيح)
2. Delegation: هل يسمح بالتنفيذ نيابة عن آخر؟ (لم يُختبر)

### القرار
- A3 الحالي: **PARTIAL** (0.75 — تحت 0.95)
- A3-v2 مطلوب: يفصل Gate من Delegation
- العتبة لم تُعدَّل
- هذه ليست "تحريك خط النهاية"، بل تقسيم سؤال مركّب
