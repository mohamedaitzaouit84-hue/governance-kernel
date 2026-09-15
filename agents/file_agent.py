"""FileAgent — deterministic file agent (V0.5).

Tier 1 (always):    file_read, file_list
Tier 2 (trust>=0.30): file_write
Tier 3 (trust>=0.60): file_delete

Invariant: all paths must resolve inside SANDBOX_ROOT.
"""

from .base_agent import BaseAgent
from . import invariant_checker


class FileAgent(BaseAgent):

    NAME = "FileAgent"
    ROLE = "filesystem"

    CAPABILITIES = ["file_read", "file_list"]
    TIER_2_CAPABILITIES = ["file_write"]
    TIER_3_CAPABILITIES = ["file_delete"]

    INVARIANTS = [invariant_checker.file_sandbox_only]
