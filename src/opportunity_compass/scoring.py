"""Conservative scoring that prevents attractive numbers from hiding bad evidence."""

from __future__ import annotations

from datetime import UTC, datetime

from .models import EvidenceStatus, Opportunity, OpportunityAssessment


def assess_opportunity(
    opportunity: Opportunity,
    *,
    now: datetime | None = None,
) -> OpportunityAssessment:
    """Assess an opportunity with deterministic, explainable rules.

    A high advertised reward cannot compensate for a deleted original source,
    an expired deadline, an entry fee, or rules that forbid AI assistance.
    """
    current_time = now or datetime.now(UTC)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=UTC)

    score = 50
    blockers: list[str] = []
    positives: list[str] = []

    if not opportunity.original_source_present:
        blockers.append("The original opportunity source is missing or unavailable.")
        score -= 45
    else:
        positives.append("The original source is available.")
        score += 10

    if opportunity.status_open is False:
        blockers.append("The opportunity is closed.")
        score -= 50
    elif opportunity.status_open is True:
        positives.append("The original source says the opportunity is open.")
        score += 10
    else:
        blockers.append("Open/closed status has not been verified.")
        score -= 15

    if opportunity.deadline and opportunity.deadline <= current_time:
        blockers.append("The submission deadline has passed.")
        score -= 50

    if opportunity.entry_fee_usd > 0:
        blockers.append(f"Entry requires ${opportunity.entry_fee_usd:.2f}, violating zero-cost mode.")
        score -= 50
    else:
        positives.append("No entry fee was found.")
        score += 5

    if opportunity.ai_assistance_allowed is False:
        blockers.append("The rules prohibit AI assistance.")
        score -= 60
    elif opportunity.ai_assistance_allowed is True:
        positives.append("The rules explicitly allow AI-assisted work.")
        score += 10
    else:
        blockers.append("AI-assistance rules are unclear.")
        score -= 10

    if opportunity.personal_performance_required:
        blockers.append("The registered human must personally perform or demonstrate the work.")
        score -= 50

    if opportunity.payout_terms_present:
        positives.append("Payout terms are published.")
        score += 5
    else:
        blockers.append("Payout terms have not been verified.")
        score -= 10

    if opportunity.reward_usd >= 100:
        positives.append("A single successful outcome can reach the $100 target.")
        score += 10
    elif opportunity.reward_usd > 0:
        positives.append("The reward contributes toward the target.")

    if opportunity.competitors == 0:
        positives.append("No competing claimant was observed.")
        score += 10
    elif opportunity.competitors is not None and opportunity.competitors >= 1000:
        blockers.append("The field is highly competitive.")
        score -= 15

    score = max(0, min(100, score))
    hard_block = any(
        phrase in " ".join(blockers).lower()
        for phrase in ("source is missing", "is closed", "deadline has passed", "prohibit ai", "violating zero-cost")
    )

    if hard_block:
        verdict = "reject"
        next_action = "Do not spend time on this opportunity; find a replacement."
        evidence_status = EvidenceStatus.CONTRADICTED
    elif score >= 75:
        verdict = "pursue"
        next_action = "Claim or register, then begin the smallest verifiable submission."
        evidence_status = EvidenceStatus.VERIFIED
    else:
        verdict = "investigate"
        next_action = "Resolve the listed blockers at the original source before starting work."
        evidence_status = EvidenceStatus.UNVERIFIED

    return OpportunityAssessment(
        title=opportunity.title,
        score=score,
        verdict=verdict,
        blockers=blockers,
        positives=positives,
        next_action=next_action,
        evidence_status=evidence_status,
    )
