# Demo script (target: 3 minutes)

## 0:00–0:25 — Problem

Show an opportunity aggregator advertising a $1,500 reward. Explain that the reward
looks compelling, but the original GitHub issue has been deleted. People can waste
hours before discovering that.

## 0:25–0:45 — Product

Show the Opportunity Compass architecture diagram. Explain that the Strands agent
collects evidence, while deterministic gates make the final decision auditable.

## 0:45–1:30 — Reproducible demo

Run:

```powershell
.venv\Scripts\opportunity-compass --score examples\first_search.json
```

Point out that the deleted $1,500 bounty is rejected despite its value. Then show the
hackathon candidate being pursued because its original rules are present, entry is
free, AI assistance is allowed, and payout terms are published.

## 1:30–2:15 — Agent tools

Open `src/opportunity_compass/tools.py` and briefly show:

- public HTTPS validation;
- private/reserved IP rejection;
- redirect-by-redirect validation;
- bounded, non-executing page extraction;
- deterministic opportunity scoring.

## 2:15–2:40 — Verification

Run:

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\ruff check .
```

Show the passing test and lint output.

## 2:40–3:00 — Close

Opportunity Compass saves people something more scarce than a bad opportunity's
advertised reward: their time. It only interrupts the human when evidence supports a
real decision.

