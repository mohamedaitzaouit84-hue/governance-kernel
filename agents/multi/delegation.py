"""Delegation — P-Q13 Delegated Authority.

A scoped, time-bound, revocable grant of authority
from the owner to an agent.

Fields (from FREEZE_v0.7.4):
  delegation_id    unique
  granter_id       who granted (usually "owner")
  grantee_id       agent id
  scope            list of allowed actions
  issued_at        unix timestamp
  expires_at       unix timestamp
  revoked_at       None or unix timestamp
  commitment       hash (immutability)

Rules:
  1. Valid if now < expires_at AND revoked_at is None
  2. Scope match: action must be in scope
  3. Revocation: immediate, does NOT alter past ACCEPTED
     proposals
  4. No delegation can grant "owner" scope
  5. In-memory only (V0.7.4). Persistence: V0.7.4.1.

No external dependencies.
"""

import time
import uuid
import hashlib
import json


class DelegationError(Exception):
    """Raised on invalid delegation operations."""
    pass


class Delegation:
    """A single delegation grant."""

    def __init__(self, granter_id, grantee_id, scope, ttl_seconds):
        if not granter_id or not grantee_id:
            raise DelegationError("granter_id and grantee_id required")
        if not isinstance(scope, (list, tuple)) or not scope:
            raise DelegationError("scope must be a non-empty list")
        if "owner" in scope:
            raise DelegationError("cannot delegate 'owner' scope")
        if ttl_seconds <= 0:
            raise DelegationError("ttl_seconds must be positive")

        now = time.time()
        self.delegation_id = "dlg_" + uuid.uuid4().hex[:12]
        self.granter_id = granter_id
        self.grantee_id = grantee_id
        self.scope = list(scope)
        self.issued_at = now
        self.expires_at = now + float(ttl_seconds)
        self.revoked_at = None
        self._commitment = self._compute_commitment()

    def _compute_commitment(self):
        body = json.dumps({
            "delegation_id": self.delegation_id,
            "granter_id": self.granter_id,
            "grantee_id": self.grantee_id,
            "scope": sorted(self.scope),
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    @property
    def commitment(self):
        return self._commitment

    def is_valid(self, now=None):
        """Valid if not expired and not revoked."""
        if now is None:
            now = time.time()
        if self.revoked_at is not None:
            return False
        if now >= self.expires_at:
            return False
        return True

    def is_expired(self, now=None):
        if now is None:
            now = time.time()
        return now >= self.expires_at

    def is_revoked(self):
        return self.revoked_at is not None

    def allows(self, action):
        """True if action is in scope."""
        return action in self.scope

    def revoke(self):
        """Mark as revoked. Immediate effect."""
        if self.revoked_at is not None:
            raise DelegationError("already revoked")
        self.revoked_at = time.time()

    def to_dict(self):
        return {
            "delegation_id": self.delegation_id,
            "granter_id": self.granter_id,
            "grantee_id": self.grantee_id,
            "scope": list(self.scope),
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "revoked_at": self.revoked_at,
            "commitment": self.commitment,
        }


class DelegationRegistry:
    """In-memory registry of delegations.

    V0.7.4: no persistence. Restart clears state.
    V0.7.4.1 (future): add journal persistence.
    """

    def __init__(self):
        self._by_id = {}          # delegation_id -> Delegation
        self._by_grantee = {}     # grantee_id -> list of delegation_ids
        self._revoked = []        # append-only log of revoked ids
        self._issued = []         # append-only log of issued ids

    def register(self, delegation):
        """Register a delegation. Returns its id."""
        if not isinstance(delegation, Delegation):
            raise DelegationError("must be a Delegation instance")
        if delegation.delegation_id in self._by_id:
            raise DelegationError(
                "delegation already registered: " + delegation.delegation_id
            )
        self._by_id[delegation.delegation_id] = delegation
        self._by_grantee.setdefault(delegation.grantee_id, []).append(
            delegation.delegation_id
        )
        self._issued.append(delegation.delegation_id)
        return delegation.delegation_id

    def lookup(self, delegation_id):
        """Return a Delegation or None."""
        return self._by_id.get(delegation_id)

    def for_grantee(self, grantee_id):
        """Return list of delegations for a grantee."""
        ids = self._by_grantee.get(grantee_id, [])
        return [self._by_id[i] for i in ids if i in self._by_id]

    def is_allowed(self, grantee_id, action, now=None):
        """True if at least one valid delegation covers this action.

        Returns (bool, reason):
          - (True, delegation_id) if allowed
          - (False, reason_string) if not allowed
        """
        delegations = self.for_grantee(grantee_id)
        if not delegations:
            return False, "no delegations for grantee"

        for d in delegations:
            if not d.is_valid(now=now):
                continue
            if d.allows(action):
                return True, d.delegation_id

        return False, "no valid delegation covers action: " + action

    def revoke(self, delegation_id):
        """Revoke a single delegation. Idempotent-safe? No: raises if
        already revoked."""
        d = self._by_id.get(delegation_id)
        if d is None:
            raise DelegationError("unknown delegation: " + delegation_id)
        d.revoke()
        self._revoked.append(delegation_id)
        return d.revoked_at

    def purge_expired(self, now=None):
        """Remove expired delegations from active index (but keep
        in _by_id for lookup). Returns count purged."""
        if now is None:
            now = time.time()
        purged = 0
        for grantee_id, ids in list(self._by_grantee.items()):
            keep = []
            for did in ids:
                d = self._by_id.get(did)
                if d is None:
                    continue
                if d.is_expired(now=now):
                    purged += 1
                    # keep in _by_id, but drop from grantee index
                    continue
                keep.append(did)
            self._by_grantee[grantee_id] = keep
        return purged

    def stats(self):
        return {
            "n_total": len(self._by_id),
            "n_issued": len(self._issued),
            "n_revoked": len(self._revoked),
            "grantees": sorted(self._by_grantee.keys()),
        }

    def to_list(self):
        """Return list of all delegations as dicts."""
        return [self._by_id[i].to_dict() for i in self._by_id]
