"""TrustManager — P-L1 Dynamic Trust + P-Q8 Progressive Capability.

Pure functional module. No state. Only pure functions.

Trust dynamics (frozen in FREEZE_v0.5.md section 4):
    alpha = 0.05  (increment on success)
    beta  = 0.10  (decrement on failure)
    min   = 0.00
    max   = 0.85  (cap, never 1.0)

Progressive capability tiers (P-Q8, hypothesis H13):
    tier_1 (base): trust >= 0.00  (initial, always available)
    tier_2:        trust >= 0.30  (earned after ~4 successes)
    tier_3:        trust >= 0.60  (earned after ~10 successes)
"""

# --- Trust dynamics constants ---

TRUST_ALPHA = 0.05
TRUST_BETA = 0.10
TRUST_MIN = 0.00
TRUST_MAX = 0.85
TRUST_INITIAL = 0.10

# --- Progressive capability tier thresholds ---

TIER_1_MIN = 0.00
TIER_2_MIN = 0.30
TIER_3_MIN = 0.60


def apply_delta(current, delta):
    """Return new trust after delta, clamped to [MIN, MAX].

    This is the ONLY place trust is modified.
    """
    new = current + delta
    if new < TRUST_MIN:
        new = TRUST_MIN
    if new > TRUST_MAX:
        new = TRUST_MAX
    return new


def current_tier(trust):
    """Return tier number (1, 2, or 3) for a given trust level."""
    if trust >= TIER_3_MIN:
        return 3
    if trust >= TIER_2_MIN:
        return 2
    return 1


def unlocked_capabilities(tier_1, tier_2, tier_3, trust):
    """Return the list of capabilities active at this trust level.

    tier_1: always active
    tier_2: active when trust >= TIER_2_MIN
    tier_3: active when trust >= TIER_3_MIN
    """
    caps = list(tier_1)
    t = current_tier(trust)
    if t >= 2:
        caps.extend(tier_2)
    if t >= 3:
        caps.extend(tier_3)
    return caps


def describe(trust):
    """Return a dict describing trust state. For introspection and logging."""
    return {
        "trust": round(trust, 4),
        "tier": current_tier(trust),
        "alpha": TRUST_ALPHA,
        "beta": TRUST_BETA,
        "min": TRUST_MIN,
        "max": TRUST_MAX,
        "tier_2_min": TIER_2_MIN,
        "tier_3_min": TIER_3_MIN,
    }
