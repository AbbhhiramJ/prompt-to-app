# Prompt → App

**Prompt → App** is an AI software factory: describe the application you want in natural language and the host agent researches it, creates a product blueprint, generates the code, tests it, repairs failures, creates a GitHub repository, deploys it, verifies the live application, and returns the URL.

## End goal

The target experience is:

```
Prompt
  ↓
Understand intent
  ↓
Adaptive online research
  ↓
Evidence-aware product blueprint
  ↓
Generate application
  ↓
Functional browser tests
  ↓
Visual desktop/mobile audit
  ↓
Repair → retest
  ↓
GitHub repository
  ↓
Vercel deployment
  ↓
Live verification
  ↓
Live URL in the same chat
```

A request such as:

> Make me a habit tracker that follows current app trends.

is only a test case. The product is the factory, not the habit tracker.

## Credential boundary

The generated application must not require:

- an LLM API key
- a GitHub token
- a Vercel token
- a Composio API key
- Ollama

Those capabilities belong to the host agent and its connected tools. The generated app is an ordinary deployable application.

## Host-agent architecture

```
Chat / Agent
   ├── Research adapter
   ├── Blueprint + planning
   ├── Code generation
   ├── GitHub adapter
   ├── Test + visual verification
   ├── Repair loop
   └── Vercel adapter
          ↓
     Generated App
          ↓
       Live URL
```

The repository contains provider-neutral contracts so GitHub, Vercel, web research, and model execution can be supplied by the connected host without coupling generated applications to those services.

## Current implementation

- adaptive bounded research
- evidence weighting
- evidence-aware product blueprint
- provider-neutral planning/generation
- functional browser tests
- desktop/mobile visual audit
- bounded repair loop
- host-agent software-factory contract
- GitHub/Vercel adapters can be injected by the host
- deployed API intentionally exposes no provider credentials or model endpoint

## Design principle

**Build the factory once; generated applications should stay simple.**

The first successful habit-tracker build proved that the generation pipeline can produce a real interactive application. The next stage is making the same pipeline reusable for arbitrary application prompts and completing the host-agent GitHub → Vercel → live-URL loop.

## GitHub + Vercel adapter (opt-in)

`prompt_to_app.github_vercel.GitHubVercelAdapter` now implements the real API boundary:

- GitHub: create **private** repository, verify its visibility, write generated files as one Git-tree commit using a non-forced ref update.
- Vercel: create a project linked to the repository, request an unpromoted preview deployment for that exact commit, poll the deployment state, then check the HTTPS site.
- The provider adapter does not execute generated code locally or include host tokens in generated files. Vercel still executes builds remotely. A trusted host must supply research/generation/test callbacks and enforce isolated execution for any untrusted tests.

**Publishing is disabled by default.** A trusted operator must explicitly opt in and provide environment secrets *outside the generated project*:

```bash
export PROMPT_TO_APP_ENABLE_PUBLISH=yes
export GITHUB_TOKEN=...            # scoped to creating/writing private repos
export VERCEL_TOKEN=...            # scoped to the intended Vercel account
export VERCEL_TEAM_ID=...          # optional team scope
```

From trusted host-only Python code:

```python
from prompt_to_app.github_vercel import GitHubVercelAdapter
from prompt_to_app.factory import SoftwareFactory

provider = GitHubVercelAdapter.from_environment()
factory = SoftwareFactory(workflow, provider.capabilities())
result = factory.build("Build a small habit tracker")
# The host is responsible for defining 'workflow' and its isolated tests.
```

No credentials or automated real-provider deployment were available during CI. Contract tests use an in-memory fake transport, and the existing CLI smoke test is local. **Do not treat this as production-ready until a controlled real GitHub/Vercel integration test, free-quota review and sandbox isolation are complete.** Failed deployments may leave a private GitHub repository and Vercel project for deliberate manual cleanup. Vercel project creation requires the account's GitHub integration to have repository access.

API references: [Vercel project creation](https://vercel.com/docs/projects/managing-projects), [Vercel deployments](https://vercel.com/docs/deployments), [GitHub Git Data API](https://docs.github.com/en/rest/git).
