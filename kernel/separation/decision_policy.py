"""DecisionPolicy — abstract interface for Policy.

Policy controls ONLY: how information is processed.
Concrete classes: SimplePolicy, AdaptivePolicy.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Decision:
    """Output of a DecisionPolicy."""
    action: float          # -1, 0, +1 in the base model
    confidence: float      # [0, 1]


class DecisionPolicy(ABC):
    """Abstract decision policy.

    A Node holds one DecisionPolicy. It does NOT know which concrete
    class it is. It only calls `decide()` and `update_state()`.
    """

    @abstractmethod
    def decide(self, info, current_state):
        """Given an InformationSet and current state, return a Decision."""
        raise NotImplementedError

    @abstractmethod
    def update_state(self, decision, info):
        """Compute the next internal state after a decision."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
