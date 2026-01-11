Discord bot for on-demand availability checks
============================================

Env variables (required):
- DISCORD_TOKEN: Bot token from Discord Developer Portal.
- GH_PAT: GitHub personal access token with repo + workflow scopes.
- GITHUB_OWNER: GitHub org/user that owns the repo.
- GITHUB_REPO: Repository name (e.g., nocker).

Optional:
- DISPATCH_EVENT: Defaults to on-demand-check to match .github/workflows/check.yml.

Install & run:
- pip install -r requirements.txt
- python bot.py

Commands in Discord:
- !check or /availability: trigger the GitHub repository_dispatch workflow.
- !help or /help: show usage info.

Notes:
- Keep tokens in environment variables only; never commit them.
- Workflow still runs hourly; alerts post only when availability is found.
