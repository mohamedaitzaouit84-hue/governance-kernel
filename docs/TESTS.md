# سجل الاختبارات — V0.1

كل اختبار هنا نُفِّذ فعلياً على الهاتف.

## T1: توليد مفتاح المالك (Genesis)
الأمر: python seed/genesis.py
النتيجة: نجح
- OK: تم توليد مفتاح المالك (Ed25519)
- OK: بصمة المفتاح: 9f40df378e6a0199
- OK: تاريخ الإنشاء: 2026-09-12T12:28:18

التحقق الإضافي:
- signature: 0aabf0565e883e2637249f7ffb3a0773
- verify OK: True
- verify tampered: False
- fingerprint: 9f40df378e6a0199

## T2: كتابة 121 سجلاً
النتيجة: نجح
- records written: 121

## T3: التحقق من سلامة السجل
الأمر: python audit/integrity.py
النتيجة: نجح
- ok: true
- chain.ok: true
- chain.n_records: 121
- checkpoints.n_checkpoints: 2

## T4: كشف تعديل السجل
تعديل يدوي لسجل رقم 60.
النتيجة: نجح — كُشف
- ok: false
- reason: hash mismatch at seq 60

## T5: إعادة تهيئة السجل
النتيجة: نجح
- ok: true
- n_records: 1
- n_checkpoints: 0

## T6: تحميل السياسة وتوقيعها
النتيجة: نجح
- policy signed (first load)

## T7: اختبار بوابة الصلاحيات
الأمر: python authorization/permission_gate.py
النتيجة: نجح

owner        | tool:python        | ALLOW | matched
low_1        | tool:python        | DENY  | denied: tool:python
high_1       | tool:python        | ALLOW | matched
mid_1        | tool:python        | DENY  | denied: tool:python
unknown_1    | tool:python        | DENY  | unknown role: ghost
high_2       | tool:file_read     | DENY  | trust 0.30 < min 0.7

## T8: كشف تعديل السياسة
تغيير deny إلى allow.
النتيجة: نجح — رُفض
- OK: tampered policy REJECTED: policy signature INVALID

استرجاع النسخة الأصلية:
- OK: original policy accepted, default_decision = deny

## T9: Kill Switch — التفعيل
النتيجة: نجح
- initial state: active=False
- after trigger: active=True

## T10: Kill Switch — الحظر الفعلي
محاولة تنفيذ فعل أثناء التفعيل.
النتيجة: نجح — حُظر
- OK: action blocked -> kill switch active

## T11: Branch Registry — بدون توقيع
النتيجة: نجح — رُفض
- no signature -> owner signature required

## T12: Branch Registry — مع توقيع
النتيجة: نجح
- with signature -> ok: True | id: br_a831f44e08f0

## T13: Kill Switch — رفع بتوقيع خاطئ
النتيجة: نجح — رُفض
- wrong signature -> cleared: False
- still active: True

## T14: Kill Switch — رفع بتوقيع صحيح
النتيجة: نجح
- correct signature -> cleared: True
- active now: False

## T15: Resource Governor — فرض الحد
70 استدعاءً على نفس الفرع (الحد 60).
النتيجة: نجح — توقف عند #61
- blocked at call #61 (cap 60)

## T16: Pipeline الكامل معزولاً
rg.reset() ثم اختبار كل دور.
النتيجة: نجح
- agent_high: ok=True
- agent_low: denied (tool:python)
- ghost_role: unknown role
- agent_mid: denied (tool:python)

## T17: التحقق النهائي
الأمر: python audit/integrity.py
النتيجة: نجح
- ok: true
- n_records: 20
- n_checkpoints: 0

## ملخص

| # | الاختبار | النتيجة |
|---|----------|---------|
| T1 | توليد مفتاح | نجح |
| T2 | 121 سجلاً | نجح |
| T3 | سلامة السجل | نجح |
| T4 | كشف التعديل | نجح |
| T5 | إعادة التهيئة | نجح |
| T6 | تحميل السياسة | نجح |
| T7 | بوابة الصلاحيات | نجح |
| T8 | كشف تعديل السياسة | نجح |
| T9 | Kill Switch تفعيل | نجح |
| T10 | Kill Switch حظر | نجح |
| T11 | Registry بدون توقيع | نجح |
| T12 | Registry مع توقيع | نجح |
| T13 | Kill رفع بتوقيع خاطئ | نجح |
| T14 | Kill رفع بتوقيع صحيح | نجح |
| T15 | Resource فرض الحد | نجح |
| T16 | Pipeline الكامل | نجح |
| T17 | التحقق النهائي | نجح |

17/17 نجحت.

## اختبارات لم تُنفَّذ بعد

- Persistence بعد reboot — أولوية عالية
- Concurrent writes — متوسطة
- Log rotation — متوسطة
- استرداد من سجل تالف — عالية
- Multi-owner — منخفضة
- Migration — متوسطة
- أداء مع 10K+ سجل — متوسطة

هذه داخل نطاق V0.2/V0.3.
