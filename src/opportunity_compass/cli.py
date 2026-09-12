"""Command-line interface for live agent and credential-free scoring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import build_agent
from .models import Opportunity
from .scoring import assess_opportunity


def _score_file(path: Path) -> int:
    raw = json.loads(path.read_text(encoding="utf-8"))
    candidates = raw if isinstance(raw, list) else [raw]
    assessments = [assess_opportunity(Opportunity.model_validate(item)) for item in candidates]
    print(json.dumps([item.model_dump(mode="json") for item in assessments], indent=2))
    return 0


def main() -> int:
    """Run the deterministic audit or the live Strands agent."""
    parser = argparse.ArgumentParser(description="Verify earning opportunities before pursuing them.")
    parser.add_argument("--score", type=Path, help="Score a JSON file without model credentials.")
    parser.add_argument("prompt", nargs="*", help="Prompt for the live Strands agent.")
    args = parser.parse_args()

    if args.score:
        return _score_file(args.score)

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        parser.error("provide --score FILE or a prompt")
    response = build_agent()(prompt)
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

