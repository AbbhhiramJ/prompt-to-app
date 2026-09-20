# Host execution contract

Prompt → App is intentionally split into a provider-neutral factory and a connected host.

## End-user flow

A user sends a natural-language request in the host chat:

`Make me a habit tracker by following current app trends`

The host is responsible for supplying connected capabilities for:

1. web research
2. model reasoning / blueprint synthesis
3. GitHub repository creation and file commits
4. Vercel project/deployment
5. live deployment verification

The generated application itself receives none of those credentials.

## Credential boundary

Generated applications must not require:

- LLM API keys
- GitHub tokens
- Vercel tokens
- Composio API keys
- Ollama

The host can use its existing connected integrations. The app is ordinary deployable source.

## Required success contract

A build is only reported as ready when:

- the generated files pass local/static validation
- functional tests pass, when enabled
- visual audit passes or its bounded repair loop is exhausted
- a GitHub commit exists
- Vercel reports the deployment as READY
- the deployment has an assigned production alias
- the host returns the live URL

An in-progress Vercel or CI state is never treated as success.

## Acceptance test

The September 20, 2026 acceptance test used a second product type, an India-focused local-first expense tracker. It produced a GitHub repository and a Vercel production deployment from a single host execution, demonstrating that the pipeline is not hard-coded to the original habit-tracker test case.

## Design rule

Build the factory once. Keep generated applications simple.