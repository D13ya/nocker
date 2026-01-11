import os
import sys
import requests
import discord

# Discord bot that triggers a GitHub repository_dispatch for on-demand checks.

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GH_PAT = os.environ.get("GH_PAT")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
DISPATCH_EVENT = os.environ.get("DISPATCH_EVENT", "on-demand-check")

missing = [name for name, val in {
    "DISCORD_TOKEN": DISCORD_TOKEN,
    "GH_PAT": GH_PAT,
    "GITHUB_OWNER": GITHUB_OWNER,
    "GITHUB_REPO": GITHUB_REPO,
}.items() if not val]

if missing:
    print(f"Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)


def trigger_dispatch():
    """Send repository_dispatch to GitHub Actions to run the monitor workflow."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GH_PAT}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"event_type": DISPATCH_EVENT}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            return "Triggered availability check. I’ll notify if slots are open."
        return f"Failed to trigger check (status {resp.status_code}): {resp.text}"
    except Exception as exc:
        return f"Error triggering check: {exc}"


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} and ready.")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip().lower()

    if content in {"!check", "/availability", "/check"}:
        reply = trigger_dispatch()
        await message.channel.send(reply)
    elif content in {"hi", "!help", "/help", "!options", "/options"}:
        await message.channel.send(
            "Commands:\n"
            "- !check (or /availability): run availability check now.\n"
            "- !help: show this help.\n"
            "Alerts only post when a slot is actually available."
        )


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
