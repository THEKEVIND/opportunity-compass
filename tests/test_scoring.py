from datetime import UTC, datetime

from opportunity_compass.models import EvidenceStatus, Opportunity
from opportunity_compass.scoring import assess_opportunity

NOW = datetime(2026, 9, 11, tzinfo=UTC)


def make_opportunity(**overrides: object) -> Opportunity:
    values: dict[str, object] = {
        "title": "Verified coding bounty",
        "source_url": "https://example.com/bounty",
        "original_url": "https://github.com/example/project/issues/1",
        "reward_usd": 120,
        "entry_fee_usd": 0,
        "status_open": True,
        "ai_assistance_allowed": True,
        "payout_terms_present": True,
        "original_source_present": True,
        "competitors": 0,
    }
    values.update(overrides)
    return Opportunity.model_validate(values)


def test_strong_candidate_is_pursued() -> None:
    result = assess_opportunity(make_opportunity(), now=NOW)

    assert result.verdict == "pursue"
    assert result.score == 100
    assert result.evidence_status == EvidenceStatus.VERIFIED


def test_missing_original_source_cannot_be_rescued_by_large_reward() -> None:
    result = assess_opportunity(
        make_opportunity(reward_usd=100_000, original_source_present=False, status_open=None),
        now=NOW,
    )

    assert result.verdict == "reject"
    assert result.evidence_status == EvidenceStatus.CONTRADICTED
    assert any("source is missing" in item for item in result.blockers)


def test_entry_fee_is_hard_block_in_zero_cost_mode() -> None:
    result = assess_opportunity(make_opportunity(entry_fee_usd=1), now=NOW)

    assert result.verdict == "reject"
    assert any("zero-cost" in item for item in result.blockers)


def test_expired_deadline_is_rejected() -> None:
    result = assess_opportunity(
        make_opportunity(deadline="2026-09-10T23:59:59Z"),
        now=NOW,
    )

    assert result.verdict == "reject"
    assert any("deadline has passed" in item for item in result.blockers)


def test_personal_performance_requirement_lowers_priority() -> None:
    result = assess_opportunity(make_opportunity(personal_performance_required=True), now=NOW)

    assert result.verdict == "investigate"
    assert any("personally perform" in item for item in result.blockers)
