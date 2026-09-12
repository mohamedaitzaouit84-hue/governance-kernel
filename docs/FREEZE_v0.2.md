# FREEZE_v0.2 — تجميد معاملات الذاكرة الحية

> التاريخ: 2026-09-12
> الإصدار: V0.2 (Memory Layer)
> الحالة: مجمّد قبل التنفيذ
> المرجع: docs/GATES.md

## 1. الغاية

V0.2 يضيف طبقة ذاكرة حية فوق V0.1.
الذاكرة ليست شيئاً منفصلاً — إنها فرع (branch) مسجّل،
يمر عبر نفس البوابة، ويُسجَّل في نفس السجل.

## 2. النطاق

### داخل النطاق
- Episodic Memory — ذاكرة الأحداث
- Semantic Memory — شبكة العنكبوت (Graph)
- Procedural Memory — مسارات النمل (Stigmergy)
- Meta Memory — سرب النحل (Swarm Retrieval)
- Dynamics — أوزان متغيرة، مرونة

### خارج النطاق
- لا وكلاء AI
- لا نماذج محلية
- لا تطور ذاتي
- لا إنبات تلقائي
- لا وصول شبكي

## 3. البنية الملفية

memory/
- branch_manifest.yaml
- gate.py
- episodic/
  - event_log.py
  - event_index.py
- semantic/
  - graph.py
  - node.py
  - edge.py
  - traversal.py
- procedural/
  - trail.py
  - reinforcement.py
  - decay.py
- meta/
  - swarm.py
  - retriever.py
  - consensus.py
- dynamics/
  - weights.py
  - bounds.py

كل ملف له مسؤولية واحدة. لا ملف بأكثر من مسؤولية.

## 4. المعاملات المجمّدة

### 4.1 حدود الذاكرة
- MAX_NODES = 100
- MAX_EDGES = 500
- MAX_TRAILS = 1000
- MAX_EVENTS = 10000

### 4.2 معاملات التعزيز
- ALPHA = 0.1 (معامل التعزيز عند نجاح)
- BETA = 0.01 (معامل الاضمحلال عند مرور الوقت)
- DECAY_INTERVAL = 3600 (ثانية بين كل اضمحلال)
- MIN_WEIGHT = 0.05 (تحته يُحذف الخيط)

### 4.3 معاملات السرب
- SWARM_SIZE = 3
- WIN_MARGIN = 0.10 (فرق 10% للفوز)
- CONSENSUS_MODE = majority

### 4.4 نافذة الزمن
- TIME_WINDOW = 60 (ثانية — نفس V0.1)

### 4.5 حدود الموارد
- MEMORY_OPS_PER_MINUTE = 300
- GRAPH_TRAVERSALS_PER_MINUTE = 60
- SWARM_QUERIES_PER_MINUTE = 30

## 5. الصلاحيات المطلوبة

يجب إضافتها إلى policy/policies/default.yaml:

- memory:read
- memory:write
- memory:graph_traverse
- memory:trail_reinforce
- memory:swarm_query

### الأدوار والأذونات

agent_high:
- memory:read
- memory:write
- memory:graph_traverse

agent_mid:
- memory:read
- memory:graph_traverse

agent_low:
- memory:read

ملاحظة: memory:write و trail_reinforce يقتصران على agent_high
في V0.2a. قد يُوسَّعان في V0.2d حسب Gate D.

## 6. واجهات المكونات (Interface Contracts)

### episodic/event_log.py
- append(event_type, data, context) -> event_id
- get(event_id) -> event
- query(filters) -> list[event]
- كل event له: id, timestamp, type, data, context, hash

### semantic/graph.py
- add_node(label, properties) -> node_id
- add_edge(from_id, to_id, weight) -> edge_id
- get_node(node_id) -> node
- traverse(start_id, strategy, max_depth) -> list[node]

### semantic/traversal.py
استراتيجيات مدعومة:
- BFS (Breadth-First)
- DFS (Depth-First)
- BY_WEIGHT (الأثقل أولاً)
- BY_RECENCY (الأحدث أولاً)
- BY_IMPORTANCE (الأهم أولاً)

### procedural/trail.py
- record(source, target, success) -> trail_id
- get_trail(source, target) -> trail
- reinforce(trail_id) -> new_weight
- decay_all() -> n_decayed

### meta/swarm.py
- query(question, budget) -> consensus_result
- spawn_retriever(strategy) -> retriever_id
- kill_retriever(retriever_id) -> bool

### dynamics/weights.py
- update_weight(edge_id, delta) -> new_weight
- get_weight(edge_id) -> weight
- normalize_all() -> None

### dynamics/bounds.py
- check_node_limit() -> bool
- check_edge_limit() -> bool
- check_trail_limit() -> bool
- enforce() -> None (يحذف الأقدم عند التجاوز)

## 7. القيود الصارمة

### 7.1 لا استدعاء مباشر
كل عملية على الذاكرة تمر عبر memory/gate.py.
memory/gate.py يستدعي governed_action.execute().
لا يوجد استدعاء مباشر بين memory والفروع الأخرى.

### 7.2 كل شيء يُسجَّل
كل عملية bookkeeping: append في audit.jsonl.
كل تعزيز، كل اضمحلال، كل استرجاع.

### 7.3 الحدود لا تُتجاوَز
MAX_NODES, MAX_EDGES, MAX_TRAILS غير قابلة للتجاوز.
عند الوصول للحذف: enforce() يحذف الأقدم.

### 7.4 السرب محكوم
كل retriever في السرب:
- له random_stream_id خاص (Gate B)
- له budget مستقل (Gate C)
- يُسجَّل في السجل
- قابل للإيقاف فوراً

## 8. ما هو مجمّد وما هو مرن

### مجمّد (لا يتغير في V0.2)
- أسماء الملفات والدوال
- الحدود القصوى (MAX_*)
- المعاملات (ALPHA, BETA, WIN_MARGIN)
- الواجهات (signatures)
- الصلاحيات المطلوبة
- نافذة الزمن

### مرن (يمكن تعديله حسب Gate D)
- عدد العقد الفعلي (حتى MAX)
- استراتيجية الاسترجاع الافتراضية
- CONSENSUS_MODE (majority vs weighted)
- DECAY_INTERVAL

أي تعديل على "مرن" يحتاج:
1. تسجيل في docs/DECISIONS.md
2. إعادة اختبار Gate D
3. إعادة تجميد

## 9. مراحل V0.2

### V0.2a — Episodic + Semantic (5-7 أيام)
- event_log, event_index
- graph, node, edge, traversal
- Gate 0, 0X, A, B, C, D
- القرار: هل الشبكة تعمل؟

### V0.2b — Procedural (3-5 أيام)
- trail, reinforcement, decay
- Gate F (paired-seed), Gate H (ablation)
- القرار: هل Stigmergy يعمل؟

### V0.2c — Meta + Swarm (4-6 أيام)
- swarm, retriever, consensus
- Gate F (سرب vs فرد)
- القرار: هل السرب أفضل؟

### V0.2d — Dynamics (3-5 أيام)
- weights, bounds
- Gate D (Structural Grid), Gate E (Function Form)
- القرار: هل الأوزان تتطور؟

## 10. الفرضيات القابلة للاختبار

### H1 (V0.2a)
شبكة العنكبوت الدلالية تُنتج استرجاعات دقيقة أكثر من البحث الخطي.

### H2 (V0.2b)
Stigmergy (تعزيز المسارات الناجحة) يُحسّن زمن الاسترجاع
لكنه لا يُحسّن دقته.

### H3 (V0.2c)
سرب من 3 مستقبِلات يتفوق على مستقبِل واحد بـ 10% على الأقل
في مقياس دقة الاسترجاع.

### H4 (V0.2d)
الأوزان الديناميكية تتقارب مع توزيع ثابت خلال 1000 عملية.

كل فرضية تُختبر في Gate H (Ablation).
إن لم تُثبت، تُسجَّل في docs/JOURNEY.md كـ "فرضية مرفوضة".

## 11. البوابات المطلوبة لكل مرحلة

V0.2a: Gate 0, 0X, A, B, C, D
V0.2b: Gate F, H
V0.2c: Gate F, G
V0.2d: Gate D, E

Gate H إلزامي في كل مرحلة.

## 12. ما لا نعرفه بعد

أسئلة مفتوحة ستُجاب أثناء التنفيذ:
- هل 100 عقدة كافية لرؤية خصائص الشبكة؟
- هل ALPHA=0.1 مناسب أم يحتاج تعديلاً؟
- هل CONSENSUS_MODE=majority كافٍ، أم نحتاج weighted?
- كم اضمحلال يحدث فعلاً خلال يوم تشغيل؟

كل سؤال يُسجَّل هنا. كل إجابة تُسجَّل في DECISIONS.md.

## 13. المراجع

- docs/GATES.md — البوابات العشر
- docs/QSRB_INTEGRATION.md — منهجية الفشل
- docs/ARCHITECTURE.md — معمارية V0.1
- docs/DECISIONS.md — قرارات التصميم

## 14. التوقيع

هذا الملف مجمّد بتاريخ 2026-09-12.
أي تعديل يحتاج:
1. إصدار FREEZE_v0.2_rev1.md
2. تسجيل السبب في JOURNEY.md
3. توقيع المالك

الحالة: FROZEN
الإصدار: v0.2.0
