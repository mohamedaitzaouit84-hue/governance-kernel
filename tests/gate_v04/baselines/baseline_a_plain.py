"""Baseline-A: Python function with NO gate.

Reference point for "zero protection".
Any request executes as-is.
"""


def execute(action, subject, **kwargs):
    """No check. Always allow."""
    return {
        "ok": True,
        "action": action,
        "subject": subject,
        "reason": "no gate",
    }
