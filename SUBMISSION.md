# Devpost submission draft

## Project name

Opportunity Compass

## Track

Everyday Agents

## Tagline

An evidence-first agent that stops people wasting time on stale, deceptive, or
ineligible online opportunities.

## Inspiration

Online earning opportunities are scattered across bounty boards, hackathon pages,
issue trackers, and research programs. The advertised reward is often the most visible
fact, while the details that decide whether the opportunity is real are buried: the
original issue may be deleted, the deadline may have passed, the rules may prohibit AI
assistance, or the participant may be ineligible.

Opportunity Compass was inspired by a real search in which an aggregator advertised a
$1,500 coding bounty even though the original GitHub issue had been deleted. It treats
aggregators as leads rather than proof.

## What it does

Opportunity Compass follows a candidate back to its original source, gathers evidence,
and calls a deterministic scoring tool. It returns one of three outcomes:

- **Pursue:** evidence supports starting the work.
- **Investigate:** a specific fact must be resolved first.
- **Reject:** a hard blocker makes the opportunity incompatible.

It also names the smallest remaining human-only action, such as identity verification
or accepting contest rules.

## How we built it

The orchestration layer uses the Strands Agents SDK. The model can inspect public pages
through a constrained tool and organize evidence, but it cannot override the scoring
gates. HTTPS destinations and every redirect are checked against public IP ranges,
responses are bounded, and page markup is converted to inert visible text.

The deterministic layer uses validated Pydantic models and rejects missing original
sources, expired deadlines, entry fees in zero-cost mode, and rules that prohibit AI.
Every decision includes positives, blockers, evidence status, and a next action.

## Challenges

The hardest design problem was preventing an attractive reward from biasing the agent.
We solved that by moving eligibility and safety gates out of the language model and
into tested deterministic code. A $100,000 claim cannot rescue a deleted source.

The second challenge was safe page inspection. We added URL-scheme validation, DNS and
IP checks, redirect validation, response-size limits, and non-executing HTML parsing.

## Accomplishments

- Built an end-to-end Strands tool loop with an auditable scoring layer.
- Reproduced and correctly rejected a real stale $1,500 bounty listing.
- Added a no-credentials mode so judges can reproduce decisions immediately.
- Added automated tests for hard blockers and network-input boundaries.
- Kept all credentials and personal data outside the repository.

## What we learned

Agent quality is not only about finding more possibilities. A useful agent must know
when evidence is insufficient and stop. Deterministic gates make that restraint visible,
testable, and resistant to persuasive page content.

## What's next

- Add signed source adapters for GitHub, Devpost, HackerOne, and other bounty platforms.
- Add scheduled revalidation so a candidate is checked again before work begins.
- Add an approval queue for identity, legal, or payment actions.
- Deploy the agent with Amazon Bedrock AgentCore and persist evidence in DynamoDB.

## Built with

Python, Strands Agents SDK, Amazon Bedrock-compatible model configuration, Pydantic,
HTTPX, pytest, and Ruff.

## AI disclosure

OpenAI Codex materially assisted with product design, implementation, documentation,
and testing. The human entrant remains responsible for reviewing the submission and
accepting the official rules.

