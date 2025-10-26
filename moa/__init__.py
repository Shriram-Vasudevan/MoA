"""Utilities for demonstrating Mixture-of-Agents concepts."""

from .aggregation import AggregationResult, aggregate_flat, aggregate_sequential
from .models import Candidate, MockModel

__all__ = [
    "AggregationResult",
    "Candidate",
    "MockModel",
    "aggregate_flat",
    "aggregate_sequential",
]
