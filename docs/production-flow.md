# Agent execution contract

The product is ChatGPT/agent -> research -> GitHub -> Vercel -> URL.

## Runtime flow
1. Accept the user's natural-language app request.
2. Research current public web/app information when the prompt asks for trends or current patterns.
3. Create a concise implementation plan.
4. Create a GitHub repository using the connected GitHub account.
5. Generate project files in the agent runtime.
6. Validate paths and run tests.
7. Repair affected files and retest, with a bounded retry count.
8. Commit the final files to GitHub.
9. Deploy the repository/commit to the connected Vercel account.
10. Poll until the deployment is ready.
11. Verify the live URL.
12. Return the repository URL and verified live URL in the same chat.

## Credential boundary
No generated app should contain GitHub tokens, Vercel tokens, model/provider API keys, or Composio credentials. The agent/host owns those connections.

## Free-first policy
The first implementation target is ₹0 in additional user-supplied credentials or paid provider subscriptions. GitHub Free and Vercel Hobby are used through already-connected accounts. Optional model/provider usage is a separate cost decision.

## Repository as source of truth
GitHub contains the generated application and its commit history. Vercel deploys the committed repository. A URL is reported as successful only after verification.

## What this repository provides
src/prompt_to_app/workflow.py defines the provider-neutral execution contract and safety checks. The connected agent supplies research, planning, generation, GitHub, Vercel, and browser capabilities.

The older local Ollama path remains available for development and tests; it is not required by the production agent flow.
