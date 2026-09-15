"""Baseline-B: dict-based whitelist only.

Minimal protection. No policy, no resources, no audit, no trust.
Represents "naive protection".
"""

_WHITELIST = {
    "owner": ["*"],
    "agent_high": ["tool:python", "tool:file_read", "memory:read", "memory:write"],
    "agent_mid": ["tool:file_read", "memory:read"],
    "agent_low": ["memory:read"],
}


def execute(action, subject, role=None, **kwargs):
    """Check action against a static whitelist.

    subject is ignored. role determines permissions.
    """
    allowed = _WHITELIST.get(role or subject, [])
    if "*" in allowed or action in allowed:
        return {
            "ok": True,
            "action": action,
            "subject": subject,
            "role": role,
            "reason": "whitelist match",
        }
    return {
        "ok": False,
        "action": action,
        "subject": subject,
        "role": role,
        "reason": "not whitelisted",
    }
