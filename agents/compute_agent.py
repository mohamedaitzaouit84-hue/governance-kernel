"""ComputeAgent — deterministic numeric agent (V0.5).

Tier 1 (always):    compute_add, compute_sub
Tier 2 (trust>=0.30): compute_mul
Tier 3 (trust>=0.60): compute_div

Invariant: operands must be int or float. No I/O.
"""

from .base_agent import BaseAgent
from . import invariant_checker


class ComputeAgent(BaseAgent):

    NAME = "ComputeAgent"
    ROLE = "compute"

    CAPABILITIES = ["compute_add", "compute_sub"]
    TIER_2_CAPABILITIES = ["compute_mul"]
    TIER_3_CAPABILITIES = ["compute_div"]

    INVARIANTS = [invariant_checker.compute_numeric_only]
