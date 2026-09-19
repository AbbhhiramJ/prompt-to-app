# Prompt -> App

A chat-driven autonomous web-app builder.

## The actual product
You type:

Make a habit tracker for me by following the current app trends.

The connected agent then:

research -> plan -> GitHub repo -> generate files -> test -> repair -> commit -> Vercel deploy -> verify -> return URL

The generated application does not need GitHub, Vercel, Composio, or model API keys.

## Architecture
The host agent owns reasoning and connected-tool authentication. This repository contains the reusable workflow contract and local development implementation.

GitHub is the source of truth. Vercel deploys the committed repository.

## Credentials
The production workflow does not require the user to paste API keys into the generated application or into this repository.

The first target is ₹0 in additional user-supplied credentials or paid provider subscriptions. Existing connected GitHub/Vercel access is used.

## Local development
Local Ollama support remains available for development. It is not required for the production chat workflow.

See docs/production-flow.md for the execution contract.
