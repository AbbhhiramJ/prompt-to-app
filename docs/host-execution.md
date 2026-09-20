# Host execution contract

## One entry point

A connected chat/agent host calls `PromptToAppHost.run(prompt)`.

The host injects `create_repository`, `write_repository`, `deploy`, and `verify_live` capabilities.
Research and model reasoning remain host capabilities through the existing workflow.
The generated application receives none of the host credentials.

## Progress

The runtime emits structured stages: understand, research, blueprint, generate, test, visual_audit, repair, github, deploy, verify_live, complete.

## Success rule

Only a FactoryResult with `status == "ready"` and a verified `live_url` represents success. In-progress CI or deployment states are never treated as success.

## User experience

The intended interaction is one natural-language prompt. The host handles orchestration and returns the repository and verified production URL.
The generated app remains an ordinary deployable application with no LLM, GitHub, Vercel, Composio, or Ollama credentials.

The runtime is provider-neutral so the same factory can be hosted by ChatGPT/Composio or another agent environment.