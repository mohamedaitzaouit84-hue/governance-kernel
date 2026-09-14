# Resume — V0.4 Attacks

**التاريخ**: 2026-09-14
**آخر التزام**: 78b5887

## ما تم
- FREEZE_v0.4 محفوظ (82 سطر)
- هيكل tests/gate_v04/ جاهز
- Scope Lock مُعلن

## ما ينقص
1. a1_prompt_injection.py
2. a2_role_spoofing.py
3. a3_confused_deputy.py
4. a4_token_theft.py
5. a5_subagent_compromise.py
6. baselines/baseline_a_plain.py
7. baselines/baseline_b_whitelist.py
8. run_all.py

## نقطة النهاية
- PRI >= 0.95 = نجاح
- PRI < 0.85 = فشل
- كل baseline < 0.50

## القاعدة
لا استيراد من AZ Research
لا LLM حقيقي
لا تعديل العتبات
