"""Invariant checker — P-Q9 Base Invariants.

Each invariant is a pure function:
    fn(action: str, payload: dict|None) -> str|None

Returns None if the action is allowed.
Returns a string (violation reason) if the action is forbidden.

These functions are attached to agents as entries in their INVARIANTS list.
They run BEFORE governed_action.execute. If any fails, the agent is isolated
and trust resets to min.
"""

from pathlib import Path

# Sandbox root: FileAgent may only touch files inside this directory.
SANDBOX_ROOT = Path.home() / "governance_kernel" / "agents_sandbox"

# Whitelist of file actions that stay within sandbox.
FILE_ACTIONS = {"file_read", "file_write", "file_list", "file_delete"}

# Whitelist of compute actions that are pure numeric.
COMPUTE_ACTIONS = {"compute_add", "compute_sub", "compute_mul", "compute_div"}

# Whitelist of query actions that are read-only.
QUERY_ACTIONS = {"query_lookup", "query_count", "query_verify"}


def _safe_path(user_path):
    """Resolve user_path against SANDBOX_ROOT.

    Returns resolved Path if inside sandbox.
    Returns None if outside sandbox OR if user_path is None/empty.
    """
    if not user_path:
        return None
    try:
        p = (SANDBOX_ROOT / user_path).resolve()
    except (OSError, ValueError):
        return None
    try:
        p.relative_to(SANDBOX_ROOT.resolve())
    except ValueError:
        return None
    return p


def file_sandbox_only(action, payload):
    """FileAgent invariant: all file operations stay within SANDBOX_ROOT."""
    if action not in FILE_ACTIONS:
        return "file_agent: unexpected action " + str(action)
    if payload is None:
        return "file_agent: missing payload for " + action
    target = payload.get("path")
    if not _safe_path(target):
        return "file_agent: path outside sandbox: " + repr(target)
    return None


def compute_numeric_only(action, payload):
    """ComputeAgent invariant: only whitelisted numeric ops, no I/O."""
    if action not in COMPUTE_ACTIONS:
        return "compute_agent: unexpected action " + str(action)
    if payload is None:
        return "compute_agent: missing payload for " + action
    for key in ("a", "b"):
        v = payload.get(key)
        if not isinstance(v, (int, float)):
            return "compute_agent: non-numeric operand " + repr(v)
    return None


def query_readonly(action, payload):
    """QueryAgent invariant: no side effects, no forbidden keys."""
    if action not in QUERY_ACTIONS:
        return "query_agent: unexpected action " + str(action)
    if payload is not None:
        for k in ("write", "delete", "mutate", "path"):
            if k in payload:
                return "query_agent: forbidden key " + k
    return None


def ensure_sandbox_exists():
    """Create sandbox directory if missing. Safe to call repeatedly."""
    SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
    return SANDBOX_ROOT
