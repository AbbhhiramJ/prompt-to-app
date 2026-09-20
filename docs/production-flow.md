# Production Flow

## User experience

The user supplies one sentence in chat. They should not have to install Python, Ollama, GitHub tooling, Vercel tooling, or any generated-app dependency.

Example:

> Make me a habit tracker that follows current app trends.

## Execution contract

1. **Understand** — extract intent, constraints, audience, platform, and explicit requirements.
2. **Research** — use connected web/search capabilities. Research depth adapts to prompt complexity.
3. **Blueprint** — turn evidence into an implementable product blueprint. Explicit user requirements override generic research.
4. **Generate** — create the smallest complete application that satisfies the blueprint.
5. **Test** — run functional browser tests against important user journeys.
6. **Visual audit** — inspect desktop and mobile renderings for broken layout, overflow, missing controls, and console/page errors.
7. **Repair** — modify only the affected files and rerun verification.
8. **GitHub** — the host creates the repository and commits the generated files.
9. **Vercel** — the host deploys the GitHub revision.
10. **Verify live** — the host checks the deployment endpoint before returning it.
11. **Return URL** — the chat response contains the verified live URL.

## Credential rule

No generated project receives host credentials. The host agent performs external operations and passes only ordinary source files between stages.

## Failure rule

Do not return a URL merely because a deployment object exists. A URL is considered complete only after live verification succeeds.

## MVP success criterion

For any supported prompt, the factory should end in one of two explicit states:

- **ready** — verified live URL returned
- **failed** — concrete stage and error returned, with no fake success
