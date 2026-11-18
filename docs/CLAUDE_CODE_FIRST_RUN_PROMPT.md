# First-run prompt for Claude Code

Open Claude Code in the extracted project folder and paste this prompt:

> Read `README.md`, `CLAUDE.md`, `docs/CONFIGURATION_CHECKLIST.md`, and the source files. Explain the architecture to me as a beginner, step by step. Help me configure this project for my Azure DevOps organization and project without asking me to paste secrets into chat. Tell me exactly which values I must enter locally in `.env`, how to create a least-privilege ADO PAT, how to verify the ADO connection, how to test Claude Code summarization, how to test SMTP email, and how to configure Windows Task Scheduler for 8:00 AM. Do not invent my organization, project, user identity, SMTP provider, or credentials. Do not modify ADO work items. Before suggesting any code change, explain why it is needed and show the exact file and section. Keep all secrets in my local `.env` file and never print them.

## Optional prompt to tune the ranking

> Review `src/ranker.py` and explain the current sort order using examples. My team needs to agree whether Bug Severity or Priority should come first, how due dates should be interpreted, and how old pending items should be handled. Propose alternatives, but do not change the code until I explicitly approve one.

## Optional prompt for a safe test run

> Help me run a dry run against a test ADO project with non-sensitive sample work items. Check the ranking, summaries, links, and email formatting. Do not send a real email until I explicitly approve the recipient and SMTP settings. Do not write or update anything in Azure DevOps.
