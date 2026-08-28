# The Undead Forest Bot 🧟☣️

A custom Discord bot for The Undead Forest 4-Day Halloween Readathon.

## Current scoring

- Clear a location/prompt: +15 points
- Extra completed book: +15 points
- Book review: +5 points
- Complete all 8 locations: +25 escape bonus
- One-time claims prevent duplicate point farming
- A single book may be used for multiple prompts
- An extra book cannot be a title already logged for a prompt
- A review can only be claimed once per title

## Render environment variables

Required:
- `DISCORD_TOKEN` — your private Discord bot token
- `GUILD_ID` — your Discord server ID (recommended while developing)
- `DATABASE_PATH` — optional; defaults to `undead_forest.db`

Never commit the Discord token to GitHub.

## Run locally

```bash
pip install -r requirements.txt
python bot.py
```
