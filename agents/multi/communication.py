"""Kernel-mediated communication channel (V0.6).

Implements principles:
  4. Clear Separation   — agents don't talk directly
  5. Double Attestation — every message logged in 2 places
  8. Prior Estimation   — no hidden buffers, all messages recorded

Every message passes through the kernel's governed_action
before being delivered. No direct agent-to-agent channel.

No external dependencies.
"""

import time
import json
import hashlib
from pathlib import Path


# Second attestation ledger for messages
_JOURNAL_PATH = Path(__file__).resolve().parent.parent.parent / "consensus" / "journal.jsonl"


class CommunicationError(Exception):
    """Raised on invalid communication operations."""
    pass


class Channel:
    """Kernel-mediated message channel.

    All messages are hashed. Delivery requires governed_action
    to succeed (caller's responsibility).
    """

    def __init__(self, branch_id):
        self.branch_id = branch_id
        self.sent = []      # messages sent by this channel
        self.received = []  # messages received by this channel

    def send(self, sender, recipient, kind, payload=None):
        """Create a signed message envelope.

        Does NOT deliver. Delivery is done by the caller after
        governed_action succeeds.
        """
        if not sender or not recipient:
            raise CommunicationError("sender and recipient required")
        if sender == recipient:
            raise CommunicationError("sender cannot be recipient")

        payload = payload or {}

        msg = {
            "sender": sender,
            "recipient": recipient,
            "kind": kind,
            "payload_keys": sorted(payload.keys()),
            "at": time.time(),
            "branch_id": self.branch_id,
        }

        # Deterministic content hash
        body = json.dumps(msg, sort_keys=True, separators=(",", ":")).encode("utf-8")
        msg["commitment"] = hashlib.sha256(body).hexdigest()

        self.sent.append(msg)
        self._attest("SENT", msg)
        return msg

    def receive(self, recipient, msg):
        """Deliver a message to recipient. Verifies commitment."""
        if msg.get("recipient") != recipient:
            raise CommunicationError(
                "message not addressed to " + recipient
            )

        # Verify commitment
        body = {
            k: v for k, v in msg.items() if k != "commitment"
        }
        body_bytes = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        expected = hashlib.sha256(body_bytes).hexdigest()

        if expected != msg.get("commitment"):
            raise CommunicationError("commitment mismatch — tampered message")

        self.received.append(msg)
        self._attest("RECEIVED", msg)
        return msg

    def _attest(self, direction, msg):
        """Write the message to the second attestation ledger."""
        record = {
            "type": "message",
            "direction": direction,
            "sender": msg["sender"],
            "recipient": msg["recipient"],
            "kind": msg["kind"],
            "commitment": msg["commitment"],
            "at": msg["at"],
        }
        _JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_JOURNAL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
