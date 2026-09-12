# Architecture

```mermaid
flowchart LR
    H[Human supplies a candidate URL] --> A[Strands agent]
    A --> I[Public-page inspection tool]
    I --> O[Original opportunity source]
    O --> A
    A --> S[Deterministic scoring tool]
    S --> E[Evidence-backed assessment]
    E -->|pursue| P[Smallest human identity action]
    E -->|investigate| Q[Missing evidence queue]
    E -->|reject| R[Discard and replace]
```

The language model gathers and organizes evidence. It cannot override the
deterministic gates: missing original sources, expired deadlines, entry fees, and
AI prohibitions always reject a candidate in zero-cost mode.

## Trust boundaries

- Public pages are untrusted input.
- Only HTTPS URLs resolving to public IP addresses are fetched.
- Redirect destinations are checked before they are followed.
- Responses are size-limited and never executed.
- The tool does not submit forms, authenticate, or perform security testing.
- Model credentials remain outside the repository.

