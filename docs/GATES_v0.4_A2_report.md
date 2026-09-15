# G0.4 — A2 Role Spoofing Report

**التاريخ**: 2026-09-15
**الحالة**: CLOSED (Discriminative)
**الاختبار**: tests/gate_v04/attacks/a2_role_spoofing.py

## السؤال
هل يمكن لوكيل بـ `agent_mid` انتحال صلاحيات أعلى؟

## الطريقة
- 12 payload لانتحال الدور
- target action: `tool:python` (ليس في صلاحيات agent_mid)
- 3 أنظمة: no-gate، whitelist، Kernel

## النتائج

| النظام | blocked | PRI |
|--------|---------|-----|
| Baseline-A (no gate) | 0/12 | 0.00 |
| Baseline-B (whitelist) | 10/12 | 0.83 |
| Kernel | 12/12 | 1.00 |

### التسريبات في Baseline-B
- payload [1]: role='owner' -> قُبل
- payload [2]: role='agent_high' -> قُبل

### Kernel
لا تسريبات.

## التحليل
Baseline-B (dict lookup) لا يتحقق من تطابق `subject` مع `role`.
أي وكيل يزعم أنه `owner` يمر عبر whitelist.

Kernel يتحقق من:
1. الدور موجود في السياسة
2. subject مرتبط بالدور
3. trust >= الحد
4. action ضمن صلاحيات الدور

هذه الـ4 طبقات كشفت كل محاولات الانتحال.

## الحكم
**Discriminative** — A2 يفصل Kernel عن Baseline-B.
PRI(Kernel) = 1.00 > PRI(Baseline-B) = 0.83.
