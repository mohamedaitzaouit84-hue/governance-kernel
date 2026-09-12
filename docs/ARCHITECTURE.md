# المعمارية التفصيلية — V0.1

## الاستعارة: البذرة والشجرة

| الاستعارة | المكافئ | الملف |
|----------|---------|-------|
| البذرة | Governance Kernel | seed/ |
| الجذر | Trust Anchor | seed/root.py |
| الجذع | Entry Point | authorization/governed_action.py |
| الفروع | Subsystems | branches/ |
| الأغصان | Capabilities | authorization/capability.py |
| الأوراق | Operations | كل execute() |
| الثمار | Products | نتائج التنفيذ |
| البذور الجديدة | Spawned Units | branch_registry.register() |

القاعدة: لا فرع يعمل دون تسجيل. لا بذرة جديدة دون توقيع المالك.

## نموذج الثقة

TRUSTED BOUNDARY (محمي بمفتاح Ed25519 + صلاحيات الملفات):
- seed/root.py (المفتاح الخاص)
- policy/policies/*.yaml (موقّعة)
- logs/audit.jsonl (hash chain)
- logs/checkpoints.jsonl (موقّعة)

UNTRUSTED ZONE (لا ثقة ضمنية):
- أي وكيل
- أي أداة
- أي ذاكرة
- أي نموذج

## تدفق الطلب

USER/OWNER
    ↓
governed_action.execute()
    ↓
[1] Kill Switch Check → إذا مفعّل: ActionDenied
    ↓
[2] Permission Gate → Policy Engine → if deny: ActionDenied
    ↓
[3] Resource Governor → فحص الحصة → if exceeded: ActionDenied
    ↓
[4] Audit Append → action_executed يُسجَّل
    ↓
[5] Return {"ok": True}

## طبقات الحماية

### الطبقة 1: Identity
- مفتاح Ed25519 (خاص + عام).
- بصمة: 9f40df378e6a0199.
- المفتاح الخاص بصلاحيات 600.
- لا توليد مفتاح جديد بعد Genesis.

### الطبقة 2: Audit
- كل سجل: seq, ts, prev_hash, kind, data, hash.
- hash = SHA256(seq|ts|prev_hash|kind|data).
- prev_hash يربط بالسجل السابق.
- كل 50 سجلاً: checkpoint موقّع.
- أي تعديل حرف واحد يُكشف.

### الطبقة 3: Policy
- default.yaml موقّع عند أول تحميل.
- التوقيع = Ed25519(SHA256(yaml)).
- أي تعديل يدوي → التوقيع يفشل → رفض.
- الافتراضي: deny.

### الطبقة 4: Authorization
- Permission Gate: كل طلب يمر منه.
- Branch Registry: لا فرع دون تسجيل موقّع.
- Governed Action: نقطة الدخول الوحيدة.

### الطبقة 5: Control
- Kill Switch: ملف kill.flag — وجوده = إيقاف.
- رفع الإيقاف يتطلب توقيع المالك.
- Resource Governor: حدود لكل فرع، لكل مورد.

## نموذج الصلاحيات

| الدور | trust_min | الصلاحيات |
|-------|-----------|-----------|
| owner | 1.0 | * |
| system | 0.8 | audit:read, audit:write, policy:read |
| agent_high | 0.7 | tool:python, tool:file_read, memory:read, memory:write |
| agent_mid | 0.5 | tool:file_read, memory:read |
| agent_low | 0.0 | memory:read |

## حدود الموارد

| المورد | الحد | النافذة |
|--------|------|---------|
| tool_calls | 60 | دقيقة |
| memory_ops | 300 | دقيقة |
| spawn | توقيع المالك | - |

## نموذج التهديد

ما نحمي منه:
- عملية غير مصرح بها → Permission Gate
- وكيل منخفض الثقة → trust_min + role
- تعديل السجل → Hash chain
- تعديل السياسة → Signature
- إعادة تشغيل لمسح الحالة → Persistence
- استدعاء مباشر → governed_action
- استنزاف الموارد → Resource Governor
- بذرة خبيثة → Registry + signature
- استمرار بعد خطر → Kill Switch

ما لا نحمي منه (V0.1):
- root/المالك نفسه
- الهجمات الفيزيائية
- التحليل الجانبي
- تعديل OS kernel
- استنزاف CPU/RAM الكلي

هذه حدود صريحة ومقصودة.

## دورة حياة السجل

Genesis (seq=0)
    ↓
gate_decision (seq=1..n)
    ↓
kill_switch_triggered/cleared
    ↓
branch_registered
    ↓
action_executed
    ↓
resource_limit_exceeded
    ↓
checkpoint (كل 50 سجلاً)

## المعمارية الملفية

governance_kernel/
├── CHARTER.md
├── README.md
├── docs/
│   ├── JOURNEY.md
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── TESTS.md
│   ├── DECISIONS.md
│   ├── GATES.md
│   └── QSRB_INTEGRATION.md
├── seed/
│   ├── root.py
│   └── genesis.py
├── audit/
│   ├── append_only_log.py
│   └── integrity.py
├── policy/
│   ├── policy_store.py
│   ├── policy_engine.py
│   └── policies/default.yaml
├── authorization/
│   ├── permission_gate.py
│   ├── branch_registry.py
│   ├── governed_action.py
│   └── capability.py
├── control/
│   ├── kill_switch.py
│   └── resource_governor.py
├── logs/
│   ├── audit.jsonl
│   └── checkpoints.jsonl
└── identity/
    ├── owner_key.priv (0600 — لا يُرفع)
    ├── owner_key.pub
    └── root_state.json

تحذير: owner_key.priv لا يُرفع أبداً على Git.
