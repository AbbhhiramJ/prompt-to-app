# Prompt -> App

A chat-driven autonomous web-app builder.

## Product flow

A short prompt is expanded through adaptive research before planning and generation.

User prompt -> intent -> adaptive research -> product/UX/visual/technical blueprint -> code generation -> functional testing -> visual audit -> repair -> GitHub -> Vercel -> live URL

## Adaptive research

Research depth is selected from the prompt itself:

- **Quick**: simple requests; small source/query budget.
- **Standard**: normal product requests; broader product, UX, visual and technical research.
- **Deep**: complex domains or prompts explicitly asking for current/trend research; adds competitor, 2026 trend, accessibility/privacy/security, onboarding/retention and differentiation research.

The research engine can also generate follow-up questions from what it has already found. It is bounded by rounds and source count so it cannot search indefinitely.

Explicit user requirements always have higher priority than research recommendations.

The host agent supplies the search callback. Generated apps do not receive search credentials, GitHub tokens, Vercel tokens, Composio credentials, or model API keys.

## Architecture

GitHub is the source of truth. Vercel deploys committed repository revisions. Local Ollama remains available for development and tests, but production reasoning belongs to the connected host agent.

The initial target remains ₹0 in additional user-supplied credentials or paid provider subscriptions.
