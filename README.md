# Prompt -> App

A chat-driven autonomous web-app builder.

## Product flow

A short user prompt is expanded through bounded immersive research before planning and generation.

User prompt -> intent -> research -> product/UX/visual/technical blueprint -> code generation -> testing -> repair -> GitHub -> Vercel -> live URL

## Immersive research

The research layer covers similar products, common features, user expectations, UX and interaction patterns, visual and responsive patterns, technical implementation patterns, accessibility, and edge cases.

Research is bounded by rounds and source count. Explicit user requirements always have higher priority than research recommendations.

The ResearchEngine is host-side infrastructure: the host agent supplies search results. Generated apps do not receive search credentials, GitHub tokens, Vercel tokens, Composio credentials, or model API keys.

## Architecture

GitHub is the source of truth. Vercel deploys committed repository revisions. Local Ollama remains available for development and tests, but production reasoning belongs to the connected host agent.

The initial target remains ₹0 in additional user-supplied credentials or paid provider subscriptions.
