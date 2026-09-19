Prompt → App

A chat-driven autonomous web-app builder.

## Product flow

User prompt → research → plan → GitHub repository → generate → test → repair → Vercel deployment → live verification → URL.

Example: “Make a habit tracker for me by following current app trends respectively.”

## Production credential policy

Production model calls use Vercel AI Gateway with the Vercel-hosted runtime identity. Vercel supports automatic OIDC authentication for deployed applications, so the production project does not need an AI Gateway API key or provider API key stored in source or environment variables.

Research/orchestration uses connected ChatGPT/Composio capabilities. GitHub and Vercel use their connected accounts. Generated applications never receive those credentials.

No additional API key is required in the production flow.

## Architecture

The existing planner, generator, verifier, browser testing, repair, and deployment components remain reusable. The production workflow contract is defined in src/prompt_to_app/workflow.py.

GitHub is the source of truth. Vercel deploys the committed repository.

## Local development

Local Ollama support remains available. A legacy OpenAI-compatible environment-key adapter is retained only for local compatibility and is not used by the production Vercel flow.

## Scope

The first production target is web applications: HTML/CSS/JavaScript and React/Next.js/Vercel-compatible projects. Arbitrary long-running Python, Java, or C++ backends require a separate sandbox/runtime layer.
