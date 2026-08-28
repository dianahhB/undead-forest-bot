import os
import re
import sqlite3
import asyncio
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# 8 Undead Forest locations/prompts
LOCATIONS = {
    1: ("🏚️", "The Abandoned Cabin", "Any book from your TBR!"),
    2: ("🎃", "Halloween Town", "Halloween-themed colors on the cover: black, orange, green, purple, or red."),
    3: ("🎢", "Tower of Terror", "A spooky genre: horror, slasher, thriller, mystery, gothic, splatterpunk, body horror, psychological horror, etc."),
    4: ("🍬", "Trick-or-Treat!", "Someone else chooses/recommends your book."),
    5: ("🔪", "The Final Girl", "A book with a strong female lead."),
    6: ("👻", "Something Wicked This Way Comes", "A book about phantoms, ghosts, or other paranormal themes."),
    7: ("🧟", "Creature Feature", "A book featuring nonhuman characters such as werewolves, vampires, zombies, etc."),
    8: ("🕯️", "Cultural Celebrations", "A book taking place in, or centered around, another culture's Halloween-like celebration."),
}

LOCATION_POINTS = 15
EXTRA_BOOK_POINTS = 15
REVIEW_POINTS = 5
ESCAPE_BONUS = 25

# ---------- Database ----------
# For Render, set DATABASE_PATH to a persistent path if using a persistent disk.
# Later we can switch this to PostgreSQL without changing the Discord commands.
DB_PATH = os.getenv("DATABASE_PATH", "undead_forest.db")
db_lock = asyncio.Lock()

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        points INTEGER NOT NULL DEFAULT 0,
        escape_bonus_claimed INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS location_claims (
        user_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        book_title TEXT NOT NULL,
        claimed_at TEXT NOT NULL,
        PRIMARY KEY (user_id, location_id)
    );

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        normalized_title TEXT NOT NULL,
        book_type TEXT NOT NULL,
        claimed_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_title TEXT NOT NULL,
        claimed_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def ensure_user(conn, user_id: int):
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().casefold())

def get_user(conn, user_id: int):
    ensure_user(conn, user_id)
    return conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()

def award_escape_bonus_if_needed(conn, user_id: int):
    completed = conn.execute(
        "SELECT COUNT(*) AS c FROM location_claims WHERE user_id = ?",
        (user_id,)
    ).fetchone()["c"]
    user = get_user(conn, user_id)
    if completed >= 8 and not user["escape_bonus_claimed"]:
        conn.execute(
            "UPDATE users SET points = points + ?, escape_bonus_claimed = 1 WHERE user_id = ?",
            (ESCAPE_BONUS, user_id)
        )
        return True
    return False

# ---------- Bot ----------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.manage_guild

async def sync_commands():
    if GUILD_ID:
        guild = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    else:
        await bot.tree.sync()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await sync_commands()
    print("Slash commands synced.")

@bot.tree.command(name="points", description="Check your Undead Forest Survival Points.")
async def points(interaction: discord.Interaction):
    async with db_lock:
        conn = connect_db()
        user = get_user(conn, interaction.user.id)
        conn.commit()
        conn.close()

    await interaction.response.send_message(
        f"☣️ **{interaction.user.display_name}'s Survival Points**\n\n"
        f"🧟 **{user['points']} points**"
    )

@bot.tree.command(name="survivor", description="View your survivor dossier and readathon progress.")
async def survivor(interaction: discord.Interaction):
    async with db_lock:
        conn = connect_db()
        user = get_user(conn, interaction.user.id)
        claims = conn.execute(
            "SELECT location_id FROM location_claims WHERE user_id = ? ORDER BY location_id",
            (interaction.user.id,)
        ).fetchall()
        extra_books = conn.execute(
            "SELECT COUNT(*) AS c FROM books WHERE user_id = ? AND book_type = 'extra'",
            (interaction.user.id,)
        ).fetchone()["c"]
        reviews = conn.execute(
            "SELECT COUNT(*) AS c FROM reviews WHERE user_id = ?",
            (interaction.user.id,)
        ).fetchone()["c"]
        conn.commit()
        conn.close()

    cleared = {row["location_id"] for row in claims}
    lines = []
    for i, (emoji, name, _) in LOCATIONS.items():
        lines.append(f"{emoji} {'✅' if i in cleared else '⬜'} {name}")

    embed = discord.Embed(
        title=f"🧟 {interaction.user.display_name}'s Survivor Dossier",
        description="\n".join(lines),
        color=discord.Color.dark_red()
    )
    embed.add_field(name="☣️ Survival Points", value=str(user["points"]))
    embed.add_field(name="📚 Extra Books", value=str(extra_books))
    embed.add_field(name="📝 Reviews", value=str(reviews))
    embed.add_field(name="🗺️ Locations", value=f"{len(cleared)}/8")
    embed.add_field(
        name="🏠 Safehouse",
        value="🔓 ESCAPED" if len(cleared) == 8 else "🔒 Locked"
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="map", description="See which Undead Forest locations you have cleared.")
async def map_command(interaction: discord.Interaction):
    async with db_lock:
        conn = connect_db()
        claims = conn.execute(
            "SELECT location_id, book_title FROM location_claims WHERE user_id = ?",
            (interaction.user.id,)
        ).fetchall()
        conn.close()

    claim_map = {row["location_id"]: row["book_title"] for row in claims}
    lines = []
    for i, (emoji, name, _) in LOCATIONS.items():
        if i in claim_map:
            lines.append(f"{emoji} **{name}** — ✅ {claim_map[i]}")
        else:
            lines.append(f"{emoji} **{name}** — ⬜ Not cleared")

    embed = discord.Embed(
        title="🗺️ THE UNDEAD FOREST — SURVIVOR MAP",
        description="\n".join(lines),
        color=discord.Color.dark_green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="complete", description="Clear a readathon location with a completed book.")
@app_commands.describe(location="The location/prompt you completed", book="The book you completed for this prompt")
async def complete(interaction: discord.Interaction, location: int, book: str):
    if location not in LOCATIONS:
        await interaction.response.send_message("⚠️ Choose a location from **1–8**.", ephemeral=True)
        return

    book = book.strip()
    if not book:
        await interaction.response.send_message("⚠️ Please enter a book title.", ephemeral=True)
        return

    async with db_lock:
        conn = connect_db()
        user_id = interaction.user.id
        ensure_user(conn, user_id)

        existing = conn.execute(
            "SELECT 1 FROM location_claims WHERE user_id = ? AND location_id = ?",
            (user_id, location)
        ).fetchone()

        if existing:
            conn.close()
            emoji, name, _ = LOCATIONS[location]
            await interaction.response.send_message(
                f"⚠️ **LOCATION ALREADY CLEARED**\n\n"
                f"{emoji} **{name}** has already been claimed by you.\n"
                f"Each location can only be claimed **once**.",
                ephemeral=True
            )
            return

        # A book can legitimately clear multiple prompts, so we do NOT block
        # a title that has already been used for another location.
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO location_claims (user_id, location_id, book_title, claimed_at) VALUES (?, ?, ?, ?)",
            (user_id, location, book, now)
        )
        conn.execute(
            "INSERT OR IGNORE INTO books (user_id, title, normalized_title, book_type, claimed_at) VALUES (?, ?, ?, 'prompt', ?)",
            (user_id, book, normalize_title(book), now)
        )
        conn.execute(
            "UPDATE users SET points = points + ? WHERE user_id = ?",
            (LOCATION_POINTS, user_id)
        )

        escape = award_escape_bonus_if_needed(conn, user_id)
        user = get_user(conn, user_id)
        conn.commit()
        conn.close()

    emoji, name, prompt = LOCATIONS[location]
    message = (
        f"☣️ **LOCATION CLEARED!**\n\n"
        f"{emoji} **{name}**\n"
        f"📖 *{book}*\n\n"
        f"🗺️ Location cleared: **+15 points**\n"
        f"☣️ Current total: **{user['points']} points**"
    )
    if escape:
        message += (
            "\n\n🏠 **SAFEHOUSE UNLOCKED!**\n"
            f"You cleared all 8 locations and earned the **+{ESCAPE_BONUS} escape bonus!**\n"
            "🧟 **SURVIVOR STATUS: ESCAPED**"
        )
    await interaction.response.send_message(message)

@bot.tree.command(name="extra-book", description="Claim points for an additional completed book.")
@app_commands.describe(book="The additional book you completed")
async def extra_book(interaction: discord.Interaction, book: str):
    book = book.strip()
    if not book:
        await interaction.response.send_message("⚠️ Please enter a book title.", ephemeral=True)
        return

    async with db_lock:
        conn = connect_db()
        user_id = interaction.user.id
        ensure_user(conn, user_id)
        norm = normalize_title(book)

        already = conn.execute(
            "SELECT 1 FROM books WHERE user_id = ? AND normalized_title = ?",
            (user_id, norm)
        ).fetchone()

        if already:
            conn.close()
            await interaction.response.send_message(
                "⚠️ **BOOK ALREADY LOGGED**\n\n"
                "That title is already being used in your readathon log. "
                "The same book cannot be claimed again as an extra book.",
                ephemeral=True
            )
            return

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO books (user_id, title, normalized_title, book_type, claimed_at) VALUES (?, ?, ?, 'extra', ?)",
            (user_id, book, norm, now)
        )
        conn.execute(
            "UPDATE users SET points = points + ? WHERE user_id = ?",
            (EXTRA_BOOK_POINTS, user_id)
        )
        user = get_user(conn, user_id)
        conn.commit()
        conn.close()

    await interaction.response.send_message(
        f"📚 **EXTRA BOOK SURVIVED!**\n\n"
        f"*{book}*\n\n"
        f"☣️ Bonus reading: **+{EXTRA_BOOK_POINTS} points**\n"
        f"🧟 Current total: **{user['points']} points**"
    )

@bot.tree.command(name="review", description="Claim points for a completed book review.")
@app_commands.describe(book="The book you reviewed")
async def review(interaction: discord.Interaction, book: str):
    book = book.strip()
    if not book:
        await interaction.response.send_message("⚠️ Please enter a book title.", ephemeral=True)
        return

    async with db_lock:
        conn = connect_db()
        user_id = interaction.user.id
        ensure_user(conn, user_id)
        norm = normalize_title(book)

        already = conn.execute(
            "SELECT 1 FROM reviews WHERE user_id = ? AND lower(book_title) = ?",
            (user_id, norm)
        ).fetchone()

        if already:
            conn.close()
            await interaction.response.send_message(
                "⚠️ **REVIEW ALREADY CLAIMED**\n\n"
                "You've already claimed review points for that title.",
                ephemeral=True
            )
            return

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO reviews (user_id, book_title, claimed_at) VALUES (?, ?, ?)",
            (user_id, book, now)
        )
        conn.execute(
            "UPDATE users SET points = points + ? WHERE user_id = ?",
            (REVIEW_POINTS, user_id)
        )
        user = get_user(conn, user_id)
        conn.commit()
        conn.close()

    await interaction.response.send_message(
        f"📝 **REVIEW LOGGED!**\n\n"
        f"*{book}*\n\n"
        f"📝 Review bonus: **+{REVIEW_POINTS} points**\n"
        f"☣️ Current total: **{user['points']} points**"
    )

@bot.tree.command(name="leaderboard", description="View the Undead Forest Survival leaderboard.")
async def leaderboard(interaction: discord.Interaction):
    async with db_lock:
        conn = connect_db()
        rows = conn.execute(
            "SELECT user_id, points FROM users WHERE points > 0 ORDER BY points DESC, user_id ASC LIMIT 25"
        ).fetchall()
        conn.close()

    if not rows:
        await interaction.response.send_message(
            "🧟 **THE SURVIVOR BOARD**\n\nNo survivors have earned points yet."
        )
        return

    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for index, row in enumerate(rows, start=1):
        member = interaction.guild.get_member(row["user_id"]) if interaction.guild else None
        name = member.display_name if member else f"Survivor {row['user_id']}"
        prefix = medals[index - 1] if index <= 3 else f"**{index}.**"
        lines.append(f"{prefix} {name} — **{row['points']} pts**")

    embed = discord.Embed(
        title="🧟 THE SURVIVOR BOARD",
        description="\n".join(lines),
        color=discord.Color.dark_red()
    )
    await interaction.response.send_message(embed=embed)

# ---------- Admin commands ----------
admin = app_commands.Group(name="admin", description="Undead Forest organizer controls.")

@admin.command(name="add-points", description="Add points to a survivor.")
@app_commands.describe(member="The survivor", amount="Points to add")
async def admin_add_points(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin(interaction):
        await interaction.response.send_message("⛔ Organizer permission required.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("⚠️ Amount must be greater than 0.", ephemeral=True)
        return

    async with db_lock:
        conn = connect_db()
        ensure_user(conn, member.id)
        conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, member.id))
        user = get_user(conn, member.id)
        conn.commit()
        conn.close()

    await interaction.response.send_message(
        f"☣️ Added **+{amount} points** to {member.mention}.\n"
        f"New total: **{user['points']}**"
    )

@admin.command(name="remove-points", description="Remove points from a survivor.")
@app_commands.describe(member="The survivor", amount="Points to remove")
async def admin_remove_points(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not is_admin(interaction):
        await interaction.response.send_message("⛔ Organizer permission required.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("⚠️ Amount must be greater than 0.", ephemeral=True)
        return

    async with db_lock:
        conn = connect_db()
        ensure_user(conn, member.id)
        conn.execute(
            "UPDATE users SET points = MAX(0, points - ?) WHERE user_id = ?",
            (amount, member.id)
        )
        user = get_user(conn, member.id)
        conn.commit()
        conn.close()

    await interaction.response.send_message(
        f"☣️ Removed **{amount} points** from {member.mention}.\n"
        f"New total: **{user['points']}**"
    )

@admin.command(name="reset", description="Reset a survivor's readathon progress.")
@app_commands.describe(member="The survivor to reset")
async def admin_reset(interaction: discord.Interaction, member: discord.Member):
    if not is_admin(interaction):
        await interaction.response.send_message("⛔ Organizer permission required.", ephemeral=True)
        return

    async with db_lock:
        conn = connect_db()
        conn.execute("DELETE FROM location_claims WHERE user_id = ?", (member.id,))
        conn.execute("DELETE FROM books WHERE user_id = ?", (member.id,))
        conn.execute("DELETE FROM reviews WHERE user_id = ?", (member.id,))
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (member.id,)
        )
        conn.execute(
            "UPDATE users SET points = 0, escape_bonus_claimed = 0 WHERE user_id = ?",
            (member.id,)
        )
        conn.commit()
        conn.close()

    await interaction.response.send_message(
        f"♻️ **SURVIVOR RESET**\n{member.mention}'s readathon progress has been reset."
    )

bot.tree.add_command(admin)

init_db()

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is missing.")

bot.run(TOKEN)
