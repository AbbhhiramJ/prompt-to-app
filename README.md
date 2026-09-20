# Prompt -> App

Prompt -> App turns a natural-language idea into a researched, planned, tested and deployable application.

## Pipeline

Prompt -> adaptive research -> evidence scoring -> AI synthesis -> App Blueprint -> generation -> functional tests -> visual audit -> repair -> GitHub -> Vercel -> live URL.

### Evidence weighting

Research sources are scored and ranked before synthesis. The score considers signals such as authoritative domains, evidence-oriented language, HTTPS, and substantive summaries. This is a heuristic, not a claim that a domain or source is automatically correct.

The blueprint receives source quality metadata so the host agent can distinguish stronger primary/official evidence from weaker secondary material. Conflicting claims should remain explicit rather than being silently averaged.

Generated applications never receive search, GitHub, Vercel, Composio, or model credentials.
