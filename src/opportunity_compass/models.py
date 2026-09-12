"""Validated data models used by the agent and deterministic scoring layer."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class EvidenceStatus(StrEnum):
    """How strongly a claim is supported by the supplied evidence."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"


class Opportunity(BaseModel):
    """Facts collected from the original opportunity and payment source."""

    title: str = Field(min_length=3, max_length=240)
    source_url: HttpUrl
    original_url: HttpUrl | None = None
    reward_usd: float = Field(ge=0, le=1_000_000)
    entry_fee_usd: float = Field(default=0, ge=0, le=100_000)
    deadline: datetime | None = None
    status_open: bool | None = None
    ai_assistance_allowed: bool | None = None
    identity_action_required: bool = False
    personal_performance_required: bool = False
    payout_terms_present: bool = False
    original_source_present: bool = False
    competitors: int | None = Field(default=None, ge=0)
    notes: list[str] = Field(default_factory=list)

    @field_validator("deadline")
    @classmethod
    def normalize_deadline(cls, value: datetime | None) -> datetime | None:
        """Make all deadlines timezone-aware so comparisons are reliable."""
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class OpportunityAssessment(BaseModel):
    """Auditable recommendation generated from an opportunity."""

    title: str
    score: int = Field(ge=0, le=100)
    verdict: str
    blockers: list[str]
    positives: list[str]
    next_action: str
    evidence_status: EvidenceStatus
