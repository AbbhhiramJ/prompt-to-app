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
