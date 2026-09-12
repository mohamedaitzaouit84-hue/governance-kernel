# Governance Kernel

نواة حكم تحكم كل ما يُبنى فوقها. V0.1 مكتمل.

## الفلسفة

بذرة واحدة. جذر راسخ. جذع يحكم. فروع مسجلة. أوراق مُسجَّلة.
لا شيء يخرج عن الجذر. لا فرع يعمل دون تسجيل.

## البنية

governance_kernel/
- CHARTER.md              — الميثاق التأسيسي
- README.md               — هذا الملف
- docs/                   — 7 وثائق مرجعية
- seed/                   — البذرة (Trust Anchor)
- audit/                  — السجل (hash-chained)
- policy/                 — السياسات (موقّعة)
- authorization/          — الصلاحيات
- control/                — التحكم (Kill Switch, Resources)
- logs/                   — السجلات المحلية
- identity/               — مفاتيح المالك (لا تُرفع)

## التشغيل الأول

cd ~/governance_kernel
python seed/genesis.py

يُشغَّل مرة واحدة فقط. يولّد مفتاح المالك Ed25519.

## اختبار النظام

python audit/integrity.py
python authorization/permission_gate.py

## المبادئ الملزمة

1. مصدر سلطة واحد — كل طلب يمر عبر governed_action.
2. السجل المرجعي — كل قرار في hash chain.
3. أقل صلاحية — لا وحدة تُمنح أكثر مما تحتاج.
4. العزل — لا استدعاء مباشر بين الفروع.
5. الفشل الآمن — الافتراضي رفض.
6. الإيقاف الفوري — Kill switch يعمل.
7. الارتباط بالجذر — كل فرع مرتبط بالبذرة.
8. الإنبات بالموافقة — لا فرع جديد دون توقيعك.

## بوابات التحقق

من V0.2 فصاعداً، كل إصدار يجتاز 10 بوابات:
Freeze, Sanity, Forensic, RNG, Budget, Grid, Function, Paired, MultTest, Ablation.
التفاصيل في docs/GATES.md.

## متطلبات التشغيل

- Python 3.10+
- cryptography
- pyyaml

يعمل بالكامل على الهاتف (Termux).

## الحالة

V0.1 مكتمل ومُختبر. 17/17 اختباراً نجحت.
V0.2 (الذاكرة الحية) قادم.

## الترخيص

خاص. جميع الحقوق محفوظة.
