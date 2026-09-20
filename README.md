# Prompt -> App

A chat-driven autonomous web-app builder.

## Product flow

User prompt -> adaptive research -> evidence-aware App Blueprint -> planning -> generation -> functional testing -> visual audit -> repair -> GitHub -> Vercel -> live URL

## Evidence-aware blueprint

Research is not passed straight into code generation as an unstructured pile of search results. It is first synthesized into explicit product decisions covering:

- core user loop
- onboarding
- logging friction
- schedule flexibility
- progress and analytics
- streak philosophy
- reminders
- integrations
- gamification
- privacy
- mobile UX
- MVP scope

A host agent can supply an AI synthesizer that compares sources and returns a richer blueprint. A deterministic fallback is included so the pipeline remains usable without another credential.

Individual product experiments are treated as evidence, not universal truth. Explicit user requirements always override research recommendations.

## Research depth

Quick, standard, and deep modes adapt the search budget to the complexity and freshness requested by the user.

## Credentials

Generated apps do not receive search credentials, GitHub tokens, Vercel tokens, Composio credentials, or model API keys. The host agent owns those capabilities.
