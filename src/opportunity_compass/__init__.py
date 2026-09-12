"""Opportunity Compass package."""

from .models import Opportunity, OpportunityAssessment
from .scoring import assess_opportunity

__all__ = ["Opportunity", "OpportunityAssessment", "assess_opportunity"]
