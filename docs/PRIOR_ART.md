# Prior Art — Honest Comparison

**Rule**: This document lists what exists BEFORE this project.
No claim of novelty is made without explicit reference here.

---

## What already exists

### Policy engines

| Project | Owner | License | Focus |
|---------|-------|---------|-------|
| Open Policy Agent (OPA) | CNCF | Apache 2.0 | General policy, Rego language |
| Cedar | AWS | Apache 2.0 | Authorization, Rust |
| Casbin | Community | Apache 2.0 | Access control, multi-language |
| Biscuit | Clever Cloud | Apache 2.0 | Tokens + authorization |

### AI safety / governance

| Project | Owner | Focus |
|---------|-------|-------|
| Constitutional AI | Anthropic | Training-time alignment |
| NeMo Guardrails | NVIDIA | LLM output filtering |
| Guardrails AI | Community | LLM validation |
| SHAP / LIME | Academia | Model explainability |

### Trust and reputation systems

| Project | Focus |
|---------|-------|
| EigenTrust | P2P reputation |
| PeerTrust | Distributed trust |
| Bayesian trust models | Theoretical |

---

## What this project does differently

**Possible novelty** (to be scrutinized):

1. **Zero-dependency governance kernel**
   - OPA/Cedar require runtimes (Go, Rust).
   - This project uses Python stdlib only.

2. **Freeze-before-code discipline**
   - Most projects code first, document later.
   - This project freezes specs before coding.

3. **Pre-registered thresholds**
   - V0.4 declared PRI target (0.95) before tests.
   - Most security projects publish numbers after the fact.

4. **P-Q11: Layered policy extension**
   - OPA has bundles, but they replace, not layer.
   - This project explicitly layers: base + extension, base untouched.

5. **Explicit failure logging (JOURNEY.md)**
   - Rare to see projects document their own failures in detail.

---

## Where this project is WEAKER

Honest assessment:

- **Maturity**: OPA has 10+ years. This project has days.
- **Adoption**: OPA used by thousands. This project by one.
- **Tooling**: OPA has debuggers, IDEs. This project has none.
- **Language**: OPA's Rego is expressive. This project uses simple YAML.
- **Community**: OPA has 1000+ contributors. This project has one.
- **Formal verification**: This project has none. Some alternatives do.
- **Production use**: None. This project has never been deployed.

---

## What this project does NOT claim

- Does not claim to replace OPA/Cedar.
- Does not claim superior security.
- Does not claim production readiness.
- Does not claim novel algorithms.
- Does not claim to be the first anything.

---

## What this project DOES claim

- That governance-first is possible at zero cost.
- That freeze-before-code produces cleaner results.
- That pre-registered thresholds change behavior.
- That documentation is a first-class artifact.
- That honesty about limits is compatible with progress.

**These claims are testable**. The evidence is in tests/gate_vNN/.
