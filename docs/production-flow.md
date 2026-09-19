# Production Prompt → App Flow

The production product is a chat-driven autonomous builder.

## Runtime

The deployed API runs on Vercel. Model calls use Vercel AI Gateway with the automatically supplied Vercel OIDC identity. No provider API key is placed in the project.

## Execution

1. Research current public web/app information.
2. Plan the application.
3. Create a GitHub repository using the connected GitHub account.
4. Generate project files and commit them to GitHub.
5. Test the generated project.
6. Repair failures and commit corrections.
7. Deploy the committed repository to Vercel.
8. Verify the live deployment.
9. Return the verified URL.

## Credential rule

No provider API key is included in this production flow. Runtime authentication uses Vercel platform OIDC for AI Gateway plus the already-connected GitHub and Vercel accounts for repository and deployment operations.

## Cost rule

No additional API-key dependency is introduced. Model usage can still incur provider/Vercel charges according to the selected model and account terms; no-key authentication does not imply universally free inference.

## Failure policy

Capture failures, repair only affected files, commit, re-test, and stop after a bounded number of attempts. Only a verified live URL is reported as successful.
