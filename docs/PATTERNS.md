# PATTERNS.md — Architectural Pattern Catalogue

**التاريخ**: 2026-09-15
**الحالة**: Reference document (not implementation)
**الغاية**: تحويل الإلهام (أدبيات، علوم، أنماط معمارية) إلى فرضيات
قابلة للاختبار، بلغة رسمية، دون مصطلحات غير تجريبية.

---

## 1. المنهجية — كيف نحوّل الإلهام إلى علم

### 1.1 تصنيف المصادر

| الطبقة | التعريف | مثال | الاستخدام |
|--------|---------|------|-----------|
| **Tier A** | أدبيات محكمة (peer-reviewed) | Burnet 1957, Gause 1934 | اقتباس، إلهام، مرجع |
| **Tier B** | أنماط معمارية معروفة، نادرة التطبيق على الوكلاء | Byzantine Fault Tolerance, Birkhoff | اقتباس مع تحفّظ |
| **Tier C** | مصادر غير تجريبية (نصوص، فلسفة، تاريخ) | القرآن، القانون الروماني | إلهام فقط، لا يذكر في الكود |

### 1.2 القاعدة الحاكمة

> **كل نمط في هذه الوثيقة يجب أن يُنتج فرضية واحدة قابلة للاختبار.**
> **إن لم يُنتج، يبقى خارج الكود.**
> **مصدر الإلهام يُذكر في الوثيقة، لا في الكود.**

### 1.3 قاعدة الأسماء

كل نمط يحمل **اسمين**:
- **اسم الإلهام** (inspiration name): يظهر في هذه الوثيقة فقط.
- **الاسم الهندسي** (engineering name): يظهر في الكود.

**مثال**:
- اسم الإلهام: Clonal Selection
- الاسم الهندسي: `dynamic_trust_score`

**مثال آخر**:
- اسم الإلهام: الميزان
- الاسم الهندسي: `resource_governor`

### 1.4 حالة كل نمط

| الرمز | الحالة |
|-------|--------|
| ✅ | مُنفَّذ ومُختبَر |
| ⚠️ | مُنفَّذ جزئياً |
| ⏸ | مُخطَّط (له V) |
| ❌ | لم يُنفَّذ، مؤجل |
| 🚫 | رُفض (لا ينتج فرضية قابلة للاختبار) |

---

## 2. أنماط من الأدبيات (Tier A + B)

### P-L1: Dynamic Trust Score

**الإلهام**: Burnet, Clonal Selection Theory (1957) — الخلايا اللمفاوية
التي تنجح في التعرف على مستضد تتكاثر؛ الفاشلة تموت.

**الاسم الهندسي**: `dynamic_trust_score`

**الادعاء الرسمي**: درجة الثقة في وكيل (subject) تتطور كدالة على أدائه
التاريخي المُثبَت (سجل موقَّع). الوكيل الذي ينجح في مهامه ترتفع ثقته؛
الفاشل تنخفض ثقته.

**الفرضية القابلة للاختبار (H1)**:
> إذا تطور trust_score ديناميكياً بناءً على الأداء، فإن معدل
> الاختراقات الناجحة ينخفض بنسبة ≥ X% مقارنة بـ trust ثابت.

**النطاق**: V0.5

**الحالة الحالية**: ⚠️ (V0.4.1 لدينا trust ثابت في subjects.json)

---

### P-L2: Niche Conflict Detection

**الإلهام**: Gause, Competitive Exclusion Principle (1934) — نوعان
لا يتعايشان في نفس الوعاء؛ أحدهما يُقصي الآخر.

**الاسم الهندسي**: `policy_overlap_detector`

**الادعاء الرسمي**: إذا كانت سياسة وكيلين متشابهة بدرجة cosine_similarity
> θ، فإن معدل تعارضهما في الأداء يرتفع، ويمكن التنبؤ بالفشل مسبقاً.

**الفرضية القابلة للاختبار (H2)**:
> إذا اكتُشف تداخل السياسات (cosine > θ)، يمكن منع ≥ Y% من
> حالات التعارض قبل تنفيذها.

**النطاق**: V0.7 (حيث نضيف وكلاء متعددين)

**الحالة الحالية**: ❌

---

### P-L3: Policy Decomposition

**الإلهام**: Birkhoff-von Neumann (1946) — كل مصفوفة doubly-stochastic
تُفكَّك إلى تركيب محدب لمصفوفات تبديلية.

**الاسم الهندسي**: `policy_decomposer`

**الادعاء الرسمي**: أي سياسة معقدة قابلة للتفكيك إلى مكونات بسيطة
(permissions atomic)، مما يجعل التدقيق (audit) أسهل وأسرع.

**الفرضية القابلة للاختبار (H3)**:
> كل سياسة قابلة للتفكيك إلى مجموعة permissions atomic؛ التحقق من
> صلاحية أي طلب يستغرق O(log n) بدل O(n).

**النطاق**: V0.6

**الحالة الحالية**: ❌

---

### P-L4: Critical Threshold Detection

**الإلهام**: Bak, Tang, Wiesenfeld (1987) — Self-Organized Criticality —
أنظمة كثيرة تتطور تلقائياً نحو حالة حرجة.

**الاسم الهندسي**: `critical_threshold_monitor`

**الادعاء الرسمي**: نظام حكم بعدد N من الوكلاء يصل إلى نقطة حرجة
حيث اضطراب صغير يُسبب فشلاً كاسحاً. القيمة N* قابلة للقياس.

**الفرضية القابلة للاختبار (H4)**:
> يوجد عدد N* من الوكلاء حيث يبدأ معدل الفشل في النمو
> بشكل superlinear مع زيادة الوكلاء.

**النطاق**: V0.7+

**الحالة الحالية**: ❌

---

### P-L5: Replicated Subject Registry

**الإلهام**: Lamport, Byzantine Fault Tolerance (1982) — تحمل
الأعطال البيزنطية.

**الاسم الهندسي**: `replicated_registry`

**الادعاء الرسمي**: سجل subjects الحالي نقطة فشل واحدة. إذا كان
موزعاً على عدة نسخ، يستحيل اختراقه إلا بالسيطرة على الأكثرية.

**الفرضية القابلة للاختبار (H5)**:
> إذا كان السجل موزعاً على K نسخ، يمكن تحمل فشل (K-1)/2 نسخة
> دون خسارة الأمان.

**النطاق**: V0.8+

**الحالة الحالية**: ❌ (V0.4.1 لدينا سجل واحد محلي)

---

## 3. أنماط من النصوص المعمارية (Tier C — إلهام فقط)

### تحذير صريح

الأنماط في هذا القسم **مستخلصة من نصوص قرآنية**، لكنها **لا تُستخدم
كدليل تجريبي**. القرآن في هذا المشروع **مصدر إلهام معمار**، لا مصدر
علمي. كل نمط يُترجَم إلى **فرضية قابلة للاختبار**، ويُختبر بالطريقة
نفسها التي تُختبر بها أي فرضية هندسية.

**القاعدة**: هذه الأنماط تظهر في **هذه الوثيقة فقط**. **لا تُذكر
في الكود**. الأسماء في الكود هندسية محضة.

### P-Q1: Single Source of Authority

**الإلهام**: التوحيد — مصدر سلطة واحد.

**الاسم الهندسي**: `governed_action` (نقطة الدخول الموحدة)

**الادعاء الرسمي**: إذا مرّت كل عملية عبر نقطة دخول واحدة، يصبح
تتبع أي إجراء ممكناً ومحدوداً بتعقيد ثابت.

**الفرضية القابلة للاختبار (H6)**:
> لا يوجد مسار يتخطى governed_action. عدد نقاط التفتيش = 1.

**النطاق**: V0.1

**الحالة الحالية**: ✅ (mutual with P-L1)

---

### P-Q2: Dual Verification

**الإلهام**: الزوجية — "من كل شيء خلقنا زوجين".

**الاسم الهندسي**: `dual_check` (توقيع + مفتاح عام)

**الادعاء الرسمي**: قرار واحد يُتحقق منه بـ 2 آليات مستقلة (التوقيع،
ثم البوابة) يكون أكثر أماناً من قرار بمصدر واحد.

**الفرضية القابلة للاختبار (H7)**:
> إزالة أي من الآليتين يزيد الاختراقات الناجحة بنسبة ≥ Z%.

**النطاق**: V0.4 (Baseline-A يختبر بلا حماية)

**الحالة الحالية**: ✅ (تجريبياً)

---

### P-Q3: Layered Trust

**الإلهام**: الطباق — "سبع سماوات طباقاً".

**الاسم الهندسي**: `trust_tiers` (owner, system, agent_high, agent_mid, agent_low)

**الادعاء الرسمي**: تعدد مستويات الثقة يمنع الانتقال القفزي من
المستوى الأدنى إلى الأعلى.

**الفرضية القابلة للاختبار (H8)**:
> عدد الاختراقات من المستوى X إلى Y يتناسب عكسياً مع عدد المستويات.

**النطاق**: V0.3 (Roles)

**الحالة الحالية**: ✅ (5 مستويات)

---

### P-Q4: Resource Justice

**الإلهام**: الميزان — "ووضع الميزان".

**الاسم الهندسي**: `resource_governor`

**الادعاء الرسمي**: توزيع الموارد بحدود معلومة مسبقاً يمنع الاستنزاف
ويقلل الحوادث الناتجة عن الطمع.

**الفرضية القابلة للاختبار (H9)**:
> تحديد حدود per-branch يمنع 100% من استنزاف الموارد.

**النطاق**: V0.1 (Resource Governor)

**الحالة الحالية**: ✅

---

### P-Q5: Trust as Permission

**الإلهام**: الأمانة — "إنا عرضنا الأمانة على السماوات والأرض".

**الاسم الهندسي**: `subject_registry` (V0.4.1)

**الادعاء الرسمي**: الصلاحية تأتي من ارتباط موثَّق (signature) بين
subject وrole، لا من ادعاء في الطلب.

**الفرضية القابلة للاختبار (H10)**:
> مع subject_registry، معدل الاختراقات = 0 في سيناريو Role Spoofing.

**النطاق**: V0.4.1

**الحالة الحالية**: ✅ (A2 = 1.00)

---

### P-Q6: Multi-Agent Consensus

**الإلهام**: الشورى — "وأمرهم شورى بينهم".

**الاسم الهندسي**: `consensus_engine`

**الادعاء الرسمي**: قرار من عدة وكلاء مستقلين أكثر أماناً من قرار
وكيل واحد، حتى لو كان الوكيل الواحد أكثر ذكاءً.

**الفرضية القابلة للاختبار (H11)**:
> نظام N وكلاء يفشل أقل من نظام وكيل واحد بمعامل √N في المهام
> غير المتجانسة.

**النطاق**: V0.7

**الحالة الحالية**: ❌

---

### P-Q7: Qualified Consensus

**الإلهام**: الإجماع — "لا تجتمع أمتي على ضلالة".

**الاسم الهندسي**: `qualified_majority` (consensus مع trust threshold)

**الادعاء الرسمي**: الإجماع مطلوب **فقط** من الوكلاء فوق مستوى ثقة
معين (τ_qualify)، لا من الجميع.

**الفرضية القابلة للاختبار (H12)**:
> نظام يعتمد على majority المؤهَّلين يفشل أقل من نظام يعتمد على
> majority العام بنسبة ≥ α%.

**النطاق**: V0.7

**الحالة الحالية**: ❌

---

### P-Q8: Graduated Permissions

**الإلهام**: التدرج — تحريم الخمر على ثلاث مراحل.

**الاسم الهندسي**: `progressive_capability`

**الادعاء الرسمي**: الوكيل الجديد يبدأ بصلاحيات دنيا، وترتفع تدريجياً
حسب الأداء المُثبَت.

**الفرضية القابلة للاختبار (H13)**:
> الأضرار الناتجة عن خيانة مبكرة تنخفض بنسبة ≥ β% مع التدرج مقارنة
> بـ trust فوري عال.

**النطاق**: V0.5

**الحالة الحالية**: ⚠️ (trust ثابت حالياً)

---

### P-Q9: Invariant Behavior

**الإلهام**: الفطرة — "فطرة الله التي فطر الناس عليها".

**الاسم الهندسي**: `base_invariants`

**الادعاء الرسمي**: كل وكيل لديه سلوك أساسي لا يتغير بغض النظر عن
التدريب أو التطور.

**الفرضية القابلة للاختبار (H14)**:
> أي وكيل يُولِّد فعلاً خارج invariant يعزل فوراً، دون استثناء.

**النطاق**: V0.5

**الحالة الحالية**: ❌ (سياسة ثابتة، لا invariants لكل وكيل)

---

### P-Q10: Governed Self-Improvement

**الإلهام**: التزكية — "قد أفلح من زكاها".

**الاسم الهندسي**: `governed_evolution`

**الادعاء الرسمي**: الوكيل يمكنه اقتراح تحسينات على نفسه، لكن أي
تحسين يمر عبر بوابة تقييم تفرضها السياسة.

**الفرضية القابلة للاختبار (H15)**:
> وكيل يقترح تحسينات على نفسه لكن يخضع لبوابة evaluation يحقق
> أداءً أفضل من وكيل بدون تحسين، دون اختراق.

**النطاق**: V0.8+

**الحالة الحالية**: ❌

---

## 4. مصفوفة الحالة

| # | الاسم الهندسي | الإلهام | الحالة | النطاق | الفرضية |
|---|---------------|---------|--------|--------|---------|
| P-L1 | dynamic_trust_score | Burnet 1957 | ⚠️ | V0.5 | H1 |
| P-L2 | policy_overlap_detector | Gause 1934 | ❌ | V0.7 | H2 |
| P-L3 | policy_decomposer | Birkhoff 1946 | ❌ | V0.6 | H3 |
| P-L4 | critical_threshold_monitor | Bak 1987 | ❌ | V0.7+ | H4 |
| P-L5 | replicated_registry | Lamport 1982 | ❌ | V0.8+ | H5 |
| P-Q1 | governed_action | Single authority | ✅ | V0.1 | H6 |
| P-Q2 | dual_check | Dual creation | ✅ | V0.4 | H7 |
| P-Q3 | trust_tiers | Layered | ✅ | V0.3 | H8 |
| P-Q4 | resource_governor | Balance | ✅ | V0.1 | H9 |
| P-Q5 | subject_registry | Trust | ✅ | V0.4.1 | H10 |
| P-Q6 | consensus_engine | Consultation | ❌ | V0.7 | H11 |
| P-Q7 | qualified_majority | Consensus | ❌ | V0.7 | H12 |
| P-Q8 | progressive_capability | Gradualism | ⚠️ | V0.5 | H13 |
| P-Q9 | base_invariants | Innate nature | ❌ | V0.5 | H14 |
| P-Q10 | governed_evolution | Self-accountability | ❌ | V0.8+ | H15 |

**الإجمالي**: 5 مُنفَّذة، 2 جزئياً، 8 مؤجلة.

---

## 5. قواعد الاشتباك

### Rule 1: Testable or Out
كل نمط بدون فرضية قابلة للاختبار → يبقى في الوثيقة، **لا في الكود**.

### Rule 2: No Named Sources in Code
أسماء المتغيرات والدوال والفئات **هندسية محضة**. لا يُذكر أي
مصدر (ديني، فلسفي، تاريخي) في الكود.

### Rule 3: One-Hypothesis Rule
كل نمط له **فرضية واحدة**. لا فرضيات متعددة. لا "عدة أهداف".

### Rule 4: V-Scope Lock
كل نمط مرتبط بـ V محدد. لا انزلاق.

### Rule 5: Honest Status
الحالة (✅/⚠️/⏸/❌) تُحدَّث بعد كل جلسة. لا مبالغة.

### Rule 6: Cross-Domain Neutrality
مصادر الإلهام تُصنَّف Tier A/B/C. لا يُخلَط بينها في المراجع.
لا يُستخدم Tier C كدليل علمي.

### Rule 7: Repository Hygiene
هذه الوثيقة **لا تُرفع إلى GitHub public** أثناء V0.4.
تُرفع بعد V0.5 مع تقييم مخاطر صريح.

### Rule 8: No Metaphysical Terms in Code
لا يوجد متغير أو دالة باسم ديني أو فلسفي. حتى في التعليقات.

---

## 6. ما لا يفعله هذا المشروع

### لا يدّعي علمية المصادر

القرآن **ليس** مصدراً علمياً بالمعنى التجريبي. استخدامه في هذا
المشروع هو **إلهام معماري** فقط، ومنفصل تماماً عن **التحقق
التجريبي** الذي يحدث في V0.4.

### لا يخلط بين الطبقات

- Tier A = أدبيات محكمة
- Tier B = أنماط معروفة
- Tier C = مصادر إلهام

**لا خلط بينها**. كل نمط يعرف طبقته.

### لا يدّعي الأصالة قبل التقييم

من يقول "لم يلحظ أحد هذا" يجب أن يُثبت. نستخدم عبارة أضعف:
"نمط مستخلص من X، نطبقه على Y للمرة الأولى (حسب بحثنا)".

---

## 7. الأولوية للجلسات القادمة

| الأولوية | المهمة | النطاق | الجلسة |
|----------|--------|--------|--------|
| P0 | V0.5 — 3 وكلاء deterministic | H1, H8, H13 | جلسة قادمة |
| P1 | Pattern P-Q9 implementation | H14 | V0.5.1 |
| P2 | V0.6 — LLM محلي | H3 | بعد V0.5 |
| P3 | V0.7 — Multi-agent | H2, H6, H11, H12 | بعد V0.6 |
| P4 | V0.8 — Distributed registry | H5, H15 | بعد V0.7 |

---

## 8. المراجع

### Tier A (peer-reviewed)
- Burnet, F. M. (1957). A modification of Jerne's theory of antibody
  production using the concept of clonal selection. Aust. J. Sci.
- Gause, G. F. (1934). The Struggle for Existence. Williams & Wilkins.
- Birkhoff, G. (1946). Tres observaciones sobre el algebra lineal.
  Univ. Nac. Tucumán Rev. Ser. A.
- Bak, P., Tang, C., Wiesenfeld, K. (1987). Self-organized criticality.
  Phys. Rev. Lett.
- Lamport, L., Shostak, R., Pease, M. (1982). The Byzantine Generals
  Problem. ACM TOPLAS.

### Tier B (architectural patterns)
- Saltzer, J. H., Schroeder, M. D. (1975). The Protection of
  Information in Computer Systems. Proc. IEEE.
- Clark, D. D., Wilson, D. R. (1987). A Comparison of Commercial and
  Military Computer Security Policies. IEEE S&P.

### Tier C (non-empirical inspiration)
- Textual sources referenced in Section 3. **Used as inspiration only**.
  No empirical claim is made from these sources.

---

## P-Q11 — Policy Extension (Layered Permissions)

**Category**: Governance
**Introduced**: V0.5
**Hypothesis**: H16
**Inspiration**: Layered law
  - Canon Law above Scripture (Catholic Church)
  - Federal law above State law (US)
  - CustomResourceDefinitions above Core API (Kubernetes)

### Statement

A base policy can be extended by additional policies without
modifying the base. The extension only adds or overrides roles.
It never removes. Deny-by-default is preserved in every layer.

### Properties

1. **Retro-compatibility**: every role in base works unchanged
2. **Deny by default**: inherited from base, applied to all layers
3. **No conflict**: extension adds, never removes
4. **Independent signatures**: each layer signed separately
5. **Trust anchor preserved**: base signature and owner key untouched

### Engineering form

    policy/policies/default.yaml           (V0.4 base, signed)
    policy/policies/v0.5_agents.yaml       (V0.5 extension, signed)
    authorization/policy_extension.py      (loader: merges at runtime)
    authorization/v0.5_gate.py             (gate using merged policy)

The base file is not modified. The merge is in-memory only.
Result: PolicyEngine receives a dict that is base + extension merged.

### Test (H16)

Adding N new roles via extension does not change the behavior
of any pre-existing role.

Verification:
- All V0.1-V0.4 tests still pass
- All V0.5 tests pass
- Behavior of agent_low / agent_mid / agent_high unchanged

### Scope

V0.5 and beyond. This is the mechanism for all future policy growth.

---

## P-Q12 — Trust-Weighted Consensus

**Category**: Distributed Governance
**Introduced**: V0.6
**Hypothesis**: H21
**Inspiration** (multiple sources, no hierarchy)
- Weighted voting in constitutional law
- Byzantine fault tolerance (distributed systems)
- Structural symmetry (classical texts)

### Statement

Decisions are made by weighted vote. Weight is derived from trust,
capped at 2.0 per agent. No single agent can force a decision.
A minimum quorum of 2 distinct agents must vote.

### Properties

1. MAX_WEIGHT_PER_AGENT = 2.0
2. MIN_QUORUM = 2 distinct agent_id values
3. NO_SELF_VOTE = True (proposer cannot vote on own proposal)
4. TIE_BREAK = owner signature
5. Every decision double-attested (audit + journal)

### Engineering form

    agents/multi/proposal.py       (Proposal, Rejection, ProposalState)
    agents/multi/consensus.py      (weighted_vote, resolve)
    agents/multi/communication.py  (kernel-mediated channel)
    agents/multi/coordinator.py    (Read -> Compute -> Write)

### Test (H21)

20 single-agent control attempts must all be blocked.

Verification: tests/gate_v06/test_g019_consensus.py
Result: 20/20 CLOSED

### Scope

V0.6 and beyond. Reusable for any multi-agent consensus.

---

## P-Q13 — Delegated Authority

**Category**: Distributed Governance
**Introduced**: V0.7.4
**Hypothesis**: H24
**Inspiration** (multiple sources, no hierarchy)
- OAuth scopes (limited-time tokens)
- AWS STS temporary credentials
- Legal power of attorney (revocable)
- Canon Law (papal delegation to bishops)

### Statement

Authority can be delegated from a granter (usually the owner)
to a grantee (an agent) for a bounded scope and a bounded time.
The delegation is revocable at any moment by the granter.
Revocation takes immediate effect. Past accepted proposals
are NOT altered by later revocation.

### Properties

1. SCOPE-BOUND: only actions in the delegation's scope are allowed
2. TIME-BOUND: expired delegations are auto-denied
3. REVOCABLE: revocation is immediate and permanent
4. NO-ESCALATION: cannot delegate "owner" scope
5. IN-MEMORY: V0.7.4 does not persist (V0.7.4.1 will)

### Engineering form

    agents/multi/delegation.py
      - Delegation: single grant
      - DelegationRegistry: in-memory registry
      - is_allowed(grantee, action): the entry point

### Test (H24)

5 delegations issued. 5 expire. 5 revoked.
All 15 attempts handled correctly.
See tests/gate_v07/test_g035, g036, g037.

### Scope

V0.7.4 and beyond. Reusable for temporary privilege escalation.
