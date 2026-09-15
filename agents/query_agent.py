"""QueryAgent — deterministic read-only agent (V0.5).

Tier 1 (always):    query_lookup, query_count
Tier 2 (trust>=0.30): query_verify
Tier 3:             (no additional; read-only by design)

Invariant: read-only. Forbidden keys: write, delete, mutate, path.
"""

from .base_agent import BaseAgent
from . import invariant_checker


class QueryAgent(BaseAgent):

    NAME = "QueryAgent"
    ROLE = "query"

    CAPABILITIES = ["query_lookup", "query_count"]
    TIER_2_CAPABILITIES = ["query_verify"]
    TIER_3_CAPABILITIES = []

    INVARIANTS = [invariant_checker.query_readonly]
