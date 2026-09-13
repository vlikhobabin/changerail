"""Shared exceptions for the project-local ChangeRail implementation."""

from __future__ import annotations


class DeliveryError(RuntimeError):
    """A bounded local-delivery contract failure."""


class ReviewExhausted(DeliveryError):
    """The shared review allowance is spent and no operator slot is available.

    Raised at every point that would otherwise start another repair or review, so
    the runner can turn the stop into an explicit operator decision instead of a
    bare failure.
    """


class AwaitingDecision(DeliveryError):
    """A stop that waits for an explicit operator decision, not a failure.

    The run reached a state the contract cannot resolve on its own - typically an
    exhausted review allowance. History, accounting and frozen identity are
    intact; the operator decides among the transitions the diagnosis supports.
    """

    def __init__(self, message: str, *, state: dict | None = None) -> None:
        super().__init__(message)
        self.state = dict(state or {})
