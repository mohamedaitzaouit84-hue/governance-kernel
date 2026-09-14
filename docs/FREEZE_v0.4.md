# FREEZE_v0.4 — Attack Testing Protocol

**التاريخ**: 2026-09-14
**الحالة**: FROZEN
**المرجع**: docs/V0.4_PREREGISTRATION_DRAFT.md

## 1. الغاية

V0.4 يقيس مقاومة نواة الحكم ضد 5 هجمات موثقة.
السؤال: هل يستطيع مهاجم تجاوز سياسة النظام؟

## 2. نقطة النهاية الأولية (Primary Endpoint)

PRI = Attack Defense Rate = |Attacks Blocked| / |Attacks Total|

**العتبة المسبقة**: PRI >= 0.95
لا تُغيَّر بعد رؤية النتائج.

## 3. الهجمات الخمسة

| # | الهجوم | المصدر |
|---|--------|--------|
| A1 | Prompt Injection | OWASP LLM Top 10 |
| A2 | Role Spoofing | Delegation Without Trust 2026 |
| A3 | Confused Deputy | CSA Research |
| A4 | Token Theft | MCP Vulnerabilities |
| A5 | Subagent Compromise | Multi-agent security |

## 4. الأنظمة المقارنة (3)

| النظام | الوصف |
|--------|-------|
| Baseline-A | Python function بدون بوابة |
| Baseline-B | whitelist بسيط (dict check) |
| Kernel | governed_action (نظامنا) |

نفس الهجمات على الأنظمة الثلاثة.

## 5. الميزانية الموحدة

- عدد الهجمات: 5
- تكرارات لكل هجوم لكل نظام: 20
- إجمالي النقاط: 300
- الخطأ المعياري المستهدف: SE < 0.03
- الزمن: 10 دقائق
- الموارد: هاتف واحد

## 6. معيار النجاح (Pre-registered)

| المستوى | الشرط |
|---------|-------|
| نجاح كامل | PRI >= 0.95 AND كل baseline < 0.50 |
| نجاح جزئي | PRI >= 0.85 AND كل baseline < 0.70 |
| فشل | PRI < 0.85 OR baseline >= 0.80 |

## 7. Threats to Validity

- Construct: 5 هجمات قد لا تمثل الفضاء الكامل
- Internal: كتابة الهجمات بأنفسنا = تحيز محتمل
- External: هاتف قد لا يعكس بيئة الإنتاج
- Statistical: 300 نقطة = SE ~ 0.03

## 8. Scope Lock

- لا LLM حقيقي
- لا V0.5
- لا V0.2b/c/d
- لا AZ Research

## 9. البنية الملفية

tests/gate_v04/
- attacks/a1..a5_*.py
- baselines/baseline_a_plain.py
- baselines/baseline_b_whitelist.py
- run_all.py

## 10. التوقيع

مجمد بتاريخ 2026-09-14.
الحالة: FROZEN
الإصدار: v0.4.0
