import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

# ============================================================
# UNDEAD FOREST SETTINGS
# ============================================================

LOCATION_STORIES = {
    1: "The trees have grown thick around an old wooden cabin. Its windows are dark, the door hangs slightly open, and something inside makes a quiet scratching sound.",
    2: "Orange lights flicker between abandoned storefronts as fog rolls through the empty streets. Jack-o'-lanterns grin from every doorstep. You hear footsteps behind you. When you turn around... nothing is there.",
    3: "The tower rises above the treeline, disappearing into the clouds. The elevator doors open by themselves. No one is inside. But the button for the top floor has already been pressed.",
    4: "A trail of glowing pumpkins winds deeper into the forest. Candy wrappers crunch beneath your feet. At the end of the path sits a basket filled with treats. There's only one problem. You don't remember putting it there.",
    5: "You find a hidden room tucked beneath an old hunting lodge. Maps cover the walls. Supplies are stacked neatly in the corner. Whoever built this place knew exactly what they were doing. Maybe you finally found somewhere safe.",
    6: "The trees suddenly open into a forgotten cemetery. Crooked headstones disappear into the fog, and candles flicker beside graves that look far too recently disturbed. Somewhere among the tombstones, you hear your name whispered.",
    7: "You stumble into a massive cavern hidden beneath the forest floor. Strange footprints cover the ground. They aren't human. And judging by the size of them... whatever made them is still nearby.",
    8: "Music drifts through the trees. Ahead, lanterns illuminate a celebration unlike anything you've seen before. People gather in costumes, sharing food, stories, and traditions passed down through generations. For the first time in the forest, you don't feel alone."
}

PROMPTS = {
    1: {
        "name": "Any Book from Your TBR!",
        "location": "The Abandoned Cabin",
        "description": "Read any book from your TBR."
    },
    2: {
        "name": "Halloween Town",
        "location": "Halloween Town",
        "description": "Read a book with Halloween-themed colors on the cover: black, orange, green, purple, or red."
    },
    3: {
        "name": "Tower of Terror",
        "location": "Tower of Terror",
        "description": "Read a spooky genre such as horror, slasher, thriller, mystery, gothic, splatterpunk, body horror, psychological horror, etc."
    },
    4: {
        "name": "Trick-or-Treat!",
        "location": "The Trick-or-Treat Trail",
        "description": "Have someone else choose your book OR read a book recommended to you."
    },
    5: {
        "name": "The Final Girl",
        "location": "The Final Girl Hideout",
        "description": "Read a book with a strong female lead."
    },
    6: {
        "name": "Something Wicked This Way Comes",
        "location": "The Haunted Cemetery",
        "description": "Read a book about phantoms, ghosts, or other paranormal themes."
    },
    7: {
        "name": "Creature Feature",
        "location": "The Creature's Lair",
        "description": "Read a book featuring nonhuman characters such as werewolves, vampires, zombies, etc."
    },
    8: {
        "name": "Cultural Celebrations",
        "location": "The Festival Grounds",
        "description": "Read a book that takes place in, or is centered around, another culture's Halloween-like celebration."
    }
}

PROMPT_POINTS = 100
LOCATION_POINTS = 25
BONUS_BOOK_POINTS = 50
SURVIVAL_TOOLS = {
    1: {
        "name": "Old Flashlight",
        "description": "A battered flashlight that still flickers to life when you need it most."
    },
    2: {
        "name": "Pumpkin Lantern",
        "description": "A strange little lantern that seems to glow brighter the deeper you go."
    },
    3: {
        "name": "Emergency Compass",
        "description": "Its needle points toward safety... most of the time."
    },
    4: {
        "name": "Trail Rope",
        "description": "Strong enough to help you navigate the forest when the trail disappears."
    },
    5: {
        "name": "First Aid Kit",
        "description": "A small emergency kit for whatever the forest throws at you."
    },
    6: {
        "name": "Grave Candle",
        "description": "Its flame refuses to go out, even in the deepest fog."
    },
    7: {
        "name": "Emergency Whistle",
        "description": "Three sharp blasts might be enough to scare off whatever is lurking nearby."
    },
    8: {
        "name": "Emergency Radio",
        "description": "A battered radio that occasionally crackles with mysterious transmissions."
    }
}

ACHIEVEMENTS = {
    "first_steps": {
        "reward": 25,
        "name": "🥾 First Steps",
        "description": "Discover your first location.",
        "type": "locations",
        "requirement": 1
    },
    "into_the_woods": {
        "reward": 25,
        "name": "🌲 Into the Woods",
        "description": "Discover 2 locations.",
        "type": "locations",
        "requirement": 2
    },
    "lost_in_the_fog": {
        "reward": 50,
        "name": "🌫️ Lost in the Fog",
        "description": "Discover 4 locations.",
        "type": "locations",
        "requirement": 4
    },
    "no_turning_back": {
        "reward": 50,
        "name": "🩸 No Turning Back",
        "description": "Discover 6 locations.",
        "type": "locations",
        "requirement": 6
    },
    "safe_at_last": {
        "reward": 100,
        "name": "🏡 Safe at Last",
        "description": "Discover all 8 locations.",
        "type": "locations",
        "requirement": 8
    },
    "prepared_survivor": {
        "reward": 25,
        "name": "🧰 Prepared Survivor",
        "description": "Collect your first Survival Tool.",
        "type": "tools",
        "requirement": 1
    },
    "pack_rat": {
        "reward": 50,
        "name": "🎒 Pack Rat",
        "description": "Collect 4 Survival Tools.",
        "type": "tools",
        "requirement": 4
    },
    "fully_equipped": {
        "reward": 100,
        "name": "🛠️ Fully Equipped",
        "description": "Collect all 8 Survival Tools.",
        "type": "tools",
        "requirement": 8
    },
    "first_blood": {
        "reward": 25,
        "name": "📖 First Blood",
        "description": "Complete your first reading prompt.",
        "type": "prompts",
        "requirement": 1
    },
    "book_survivor": {
        "reward": 50,
        "name": "📚 Book Survivor",
        "description": "Complete 4 reading prompts.",
        "type": "prompts",
        "requirement": 4
    },
    "undead_reader": {
        "reward": 100,
        "name": "☣️ Undead Reader",
        "description": "Complete all 8 reading prompts.",
        "type": "prompts",
        "requirement": 8
    },
    "beyond_the_grave": {
        "reward": 25,
        "name": "⭐ Beyond the Grave",
        "description": "Complete your first Bonus Book.",
        "type": "bonus_books",
        "requirement": 1
    },
    "book_hoarder": {
        "reward": 50,
        "name": "📚 Book Hoarder",
        "description": "Complete 5 Bonus Books.",
        "type": "bonus_books",
        "requirement": 5
    },
    "undead_survivor": {
        "reward": 200,
        "name": "👑 The Undead Survivor",
        "description": "Complete the entire Undead Forest.",
        "type": "locations",
        "requirement": 8
    }
}


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "undead_forest.db"


def get_db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            prompt_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, user_id, prompt_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bonus_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, user_id, book_title)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survival_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            tool_id INTEGER NOT NULL,
            tool_name TEXT NOT NULL,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, user_id, tool_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            achievement_name TEXT NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, user_id, achievement_id)
        )
    """)

    connection.commit()
    connection.close()


def ensure_player(guild_id, user_id, username):

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO players
        (guild_id, user_id, username, points)
        VALUES (?, ?, ?, 0)

        ON CONFLICT(guild_id, user_id)
        DO UPDATE SET username = excluded.username
    """, (
        guild_id,
        user_id,
        username
    ))

    connection.commit()
    connection.close()


# ============================================================
# BOT
# ============================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ============================================================
# READY
# ============================================================

def check_achievements(guild_id, user_id):
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
    """, (guild_id, user_id))
    location_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM survival_tools
        WHERE guild_id = ?
        AND user_id = ?
    """, (guild_id, user_id))
    tool_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
    """, (guild_id, user_id))
    prompt_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bonus_books
        WHERE guild_id = ?
        AND user_id = ?
    """, (guild_id, user_id))
    bonus_count = cursor.fetchone()[0]

    unlocked = []

    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement["type"] == "locations":
            current = location_count
        elif achievement["type"] == "tools":
            current = tool_count
        elif achievement["type"] == "prompts":
            current = prompt_count
        elif achievement["type"] == "bonus_books":
            current = bonus_count
        else:
            continue

        if current < achievement["requirement"]:
            continue

        cursor.execute("""
            INSERT OR IGNORE INTO achievements
            (guild_id, user_id, achievement_id, achievement_name)
            VALUES (?, ?, ?, ?)
        """, (
            guild_id,
            user_id,
            achievement_id,
            achievement["name"]
        ))

        if cursor.rowcount > 0:
            reward = achievement.get("reward", 0)

            if reward > 0:
                cursor.execute("""
                    UPDATE players
                    SET points = points + ?
                    WHERE guild_id = ?
                    AND user_id = ?
                """, (
                    reward,
                    guild_id,
                    user_id
                ))

            unlocked.append(achievement)

    connection.commit()
    connection.close()

    return unlocked


@bot.event
async def on_ready():

    setup_database()

    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")

    try:

        # synced = await bot.tree.sync()

        test_guild = discord.Object(id=1543413824420315187)
        bot.tree.copy_global_to(guild=test_guild)
        test_synced = await bot.tree.sync(guild=test_guild)

        ###
        print(
            f"Synced {len(synced)} global slash commands."
        )
        ###


        print(
            f"Synced {len(test_synced)} test_server slash commands/"
        )


    except Exception as error:
        print(
            f"Command sync error: {error}"
        )

# ============================================================
# PROFILE
# ============================================================

@bot.tree.command(
    name="profile",
    description="View your Undead Forest survivor profile."
)
async def profile(
    interaction: discord.Interaction
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "☣️ This command can only be used inside a server.",
            ephemeral=True
        )

        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    ensure_player(
        guild_id,
        user_id,
        interaction.user.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT points
        FROM players
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    player = cursor.fetchone()

    cursor.execute("""
        SELECT prompt_id, book_title
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
        ORDER BY prompt_id
    """, (
        guild_id,
        user_id
    ))

    claims = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM bonus_books
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    bonus_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM survival_tools
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))
    tool_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM achievements
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))
    achievement_count = cursor.fetchone()[0]


    connection.close()

    embed = discord.Embed(
        title="🧟 Survivor Profile",
        description=(
            f"**{interaction.user.display_name}**"
        ),
        color=discord.Color.dark_red()
    )

    embed.add_field(
        name="☣️ Survival Points",
        value=f"**{player['points']}**",
        inline=True
    )

    embed.add_field(
        name="🗺️ Locations",
        value=f"**{len(claims)} / 8**",
        inline=True
    )

    embed.add_field(
        name="⭐ Bonus Books",
        value=f"**{bonus_count}**",
        inline=True
    )

    embed.add_field(
        name="🧰 Survival Tools",
        value=f"**{tool_count}/8**",
        inline=True
    )

    embed.add_field(
        name="🏆 Achievements",
        value=f"**{achievement_count}/{len(ACHIEVEMENTS)}**",
        inline=True
    )

    if claims:

        locations = "\n".join(
            f"🟢 {PROMPTS[row['prompt_id']]['location']}"
            for row in claims
        )

        embed.add_field(
            name="📍 Discovered Locations",
            value=locations,
            inline=False
        )

    if len(claims) == 8:

        embed.add_field(
            name="🏠 SAFEHOUSE",
            value="🔓 **ESCAPED THE UNDEAD FOREST**",
            inline=False
        )

    else:

        embed.add_field(
            name="🏠 SAFEHOUSE",
            value="🔒 Still locked...",
            inline=False
        )

        await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# LOCATIONS
# ============================================================

@bot.tree.command(
    name="locations",
    description="View the locations you have discovered."
)
async def locations(
    interaction: discord.Interaction
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "☣️ Use this command inside a server.",
            ephemeral=True
        )

        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT prompt_id
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    claimed = {
        row["prompt_id"]
        for row in cursor.fetchall()
    }

    connection.close()

    lines = []

    for number, prompt in PROMPTS.items():

        if number in claimed:

            lines.append(
                f"🟢 **{prompt['location']}** — DISCOVERED"
            )

        else:

            lines.append(
                f"⚫ **{prompt['location']}** — UNKNOWN"
            )

    embed = discord.Embed(
        title="🗺️ THE UNDEAD FOREST",
        description="\n".join(lines),
        color=discord.Color.dark_red()
    )

    embed.set_footer(
        text=f"{len(claimed)} / 8 locations discovered"
    )

    await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# CLAIM PROMPT
# ============================================================

@bot.tree.command(
    name="claim",
    description="Claim a completed readathon prompt."
)
@app_commands.describe(
    prompt="Prompt number (1-8)",
    book="The completed book title"
)
async def claim(
    interaction: discord.Interaction,
    prompt: app_commands.Range[int, 1, 8],
    book: str
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "☣️ Use this command inside a server.",
            ephemeral=True
        )

        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    book = book.strip()

    if not book:

        await interaction.response.send_message(
            "⚠️ Please enter a book title.",
            ephemeral=True
        )

        return

    ensure_player(
        guild_id,
        user_id,
        interaction.user.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
        AND prompt_id = ?
    """, (
        guild_id,
        user_id,
        prompt
    ))

    existing = cursor.fetchone()

    if existing:

        connection.close()

        await interaction.response.send_message(
            f"🔒 **PROMPT ALREADY CLAIMED**\n\n"
            f"You've already completed:\n"
            f"**{PROMPTS[prompt]['name']}**\n\n"
            f"Each prompt can only be claimed once.",
            ephemeral=True
        )

        return

    cursor.execute("""
        INSERT INTO claims
        (guild_id, user_id, prompt_id, book_title)
        VALUES (?, ?, ?, ?)
    """, (
        guild_id,
        user_id,
        prompt,
        book
    ))

    cursor.execute("""
        UPDATE players
        SET points = points + ?
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        PROMPT_POINTS,
        guild_id,
        user_id
    ))

    cursor.execute("""
        UPDATE players
        SET points = points + ?
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        LOCATION_POINTS,
        guild_id,
        user_id
    ))

    tool = SURVIVAL_TOOLS.get(prompt)
    tool_awarded = False

    if tool:
        cursor.execute("""
            INSERT OR IGNORE INTO survival_tools
            (guild_id, user_id, tool_id, tool_name)
            VALUES (?, ?, ?, ?)
        """, (
            guild_id,
            user_id,
            prompt,
            tool["name"]
        ))
        tool_awarded = cursor.rowcount > 0

    connection.commit()

    cursor.execute("""
        SELECT points
        FROM players
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    total_points = cursor.fetchone()["points"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    completed_count = cursor.fetchone()[0]

    newly_unlocked = check_achievements(guild_id, user_id)

    connection.close()

    embed = discord.Embed(
        title="🗺️ LOCATION DISCOVERED!",
        description=(
            f"**{interaction.user.display_name}** "
            f"has survived another section of the forest.\n\n"
        f"{LOCATION_STORIES.get(prompt, '')}"
        ),
        color=discord.Color.dark_red()
    )

    if tool_awarded:
        embed.add_field(
            name="🧰 SURVIVAL TOOL FOUND!",
            value=(
                f"**{tool['name']}**\n"
                f"*{tool['description']}*\n\n"
                "**Added to your Survival Pack.**"
            ),
            inline=False
        )

    if newly_unlocked:
        achievement_text = "\n".join(
            f"🏆 **{achievement['name']}**\n"
            f"*{achievement['description']}*\n"
            f"💰 **+{achievement.get('reward', 0)} Survival Points**"
            for achievement in newly_unlocked
        )

        embed.add_field(
            name="🏆 ACHIEVEMENT UNLOCKED!",
            value=achievement_text,
            inline=False
        )

    embed.add_field(
        name="📖 Prompt",
        value=(
            f"**{prompt}. {PROMPTS[prompt]['name']}**\n"
            f"{PROMPTS[prompt]['description']}"
        ),
        inline=False
    )

    embed.add_field(
        name="📚 Book Completed",
        value=book,
        inline=False
    )

    embed.add_field(
        name="🗺️ Location",
        value=f"**{PROMPTS[prompt]['location']}**",
        inline=False
    )

    embed.add_field(
        name="☣️ Points Earned",
        value=(
            f"📖 Prompt: **+{PROMPT_POINTS}**\n"
            f"🗺️ Location: **+{LOCATION_POINTS}**\n"
            f"⭐ Total earned: **+{PROMPT_POINTS + LOCATION_POINTS}**"
        ),
        inline=False
    )

    embed.add_field(
        name="☣️ Survival Points",
        value=f"**{total_points}**",
        inline=True
    )

    embed.add_field(
        name="🗺️ Forest Progress",
        value=f"**{completed_count}/8**",
        inline=True
    )

    if completed_count == 8:

        embed.add_field(
            name="🏡 SAFEHOUSE UNLOCKED!",
            value=(
                "You made it.\n\n"
                "After days of wandering through the forest, the trees finally "
                "give way to a small cabin glowing warmly against the darkness.\n\n"
                "The door is unlocked.\n\n"
                "Inside, there's a fireplace, blankets, food, and enough supplies "
                "to finally breathe.\n\n"
                "**For the first time since entering the forest... you're safe.**\n\n"
                "🌲 **THE UNDEAD FOREST — SURVIVED**\n\n"
                f"🗺️ Locations Discovered: **{completed_count}/8**\n"
                f"☣️ Survival Points: **{total_points}**\n\n"
                "🔓 **SAFEHOUSE UNLOCKED**"
            ),
            inline=False
        )

    await interaction.response.send_message(
            embed=embed
        )



# ============================================================
# SAFEHOUSE
# ============================================================

@bot.tree.command(
    name="achievements",
    description="View your Undead Forest achievements."
)
async def achievements(interaction: discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
            "🏆 This command can only be used inside a server.",
            ephemeral=True
        )
        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    ensure_player(
        guild_id,
        user_id,
        interaction.user.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT achievement_id
        FROM achievements
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    unlocked_ids = {
        row["achievement_id"]
        for row in cursor.fetchall()
    }

    cursor.close()
    connection.close()

    unlocked = []
    locked = []

    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id in unlocked_ids:
            unlocked.append(
                f"🟢 **{achievement['name']}**\n"
                f"*{achievement['description']}*"
            )
        else:
            locked.append(
                f"🔒 **{achievement['name']}**\n"
                f"*{achievement['description']}*"
            )

    total = len(ACHIEVEMENTS)
    unlocked_count = len(unlocked_ids & set(ACHIEVEMENTS.keys()))

    embed = discord.Embed(
        title="🏆 YOUR ACHIEVEMENTS",
        description=(
            f"**{interaction.user.display_name}**\n\n"
            f"🏆 **Progress: {unlocked_count}/{total} unlocked**"
        ),
        color=discord.Color.dark_green()
    )

    if unlocked:
        embed.add_field(
            name="✨ Unlocked",
            value="\n\n".join(unlocked),
            inline=False
        )

    if locked:
        embed.add_field(
            name="🔒 Still to Earn",
            value="\n\n".join(locked),
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="survivalpack",
    description="View your Undead Forest Survival Pack."
)
async def survivalpack(interaction: discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
            "🧰 This command can only be used inside a server.",
            ephemeral=True
        )
        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    ensure_player(
        guild_id,
        user_id,
        interaction.user.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT tool_id, tool_name
        FROM survival_tools
        WHERE guild_id = ?
        AND user_id = ?
        ORDER BY tool_id
    """, (
        guild_id,
        user_id
    ))

    collected = cursor.fetchall()

    cursor.close()
    connection.close()

    collected_ids = {row["tool_id"] for row in collected}

    collected_text = []
    locked_text = []

    for tool_id, tool in SURVIVAL_TOOLS.items():
        if tool_id in collected_ids:
            collected_text.append(
                f"🟢 **{tool['name']}**\n"
                f"*{tool['description']}*"
            )
        else:
            locked_text.append(
                f"🔒 **{tool['name']}**"
            )

    embed = discord.Embed(
        title="🧰 YOUR SURVIVAL PACK",
        description=(
            f"**{interaction.user.display_name}**\n\n"
            f"🧰 **Tools Collected: "
            f"{len(collected_ids)}/{len(SURVIVAL_TOOLS)}**"
        ),
        color=discord.Color.dark_green()
    )

    if collected_text:
        embed.add_field(
            name="🎒 Collected",
            value="\n\n".join(collected_text),
            inline=False
        )
    else:
        embed.add_field(
            name="🎒 Collected",
            value="*Your pack is empty... for now.*",
            inline=False
        )

    if locked_text:
        embed.add_field(
            name="🌲 Still Out There",
            value="\n".join(locked_text),
            inline=False
        )

    if len(collected_ids) == len(SURVIVAL_TOOLS):
        embed.add_field(
            name="🛠️ FULLY EQUIPPED",
            value="**You've collected every Survival Tool in the forest.**",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="safehouse",
    description="Enter your Safehouse after surviving the Undead Forest."
)
async def safehouse(interaction: discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
            "🏡 This command can only be used inside a server.",
            ephemeral=True
        )
        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    ensure_player(
        guild_id,
        user_id,
        interaction.user.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT points
        FROM players
        WHERE guild_id = ?
        AND user_id = ?
        """,
        (guild_id, user_id)
    )

    player = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM claims
        WHERE guild_id = ?
        AND user_id = ?
        """,
        (guild_id, user_id)
    )

    completed_count = cursor.fetchone()[0]

    connection.close()

    if completed_count < 8:
        embed = discord.Embed(
            title="🔒 SAFEHOUSE LOCKED",
            description=(
                f"**{interaction.user.display_name}**, you haven't survived "
                "the entire forest yet.\n\n"
                f"🌲 Forest Progress: **{completed_count}/8**\n\n"
                "Complete all 8 locations to unlock the Safehouse.\n\n"
                "*Keep going, survivor...* 🌲"
            ),
            color=discord.Color.dark_red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        return

    total_points = player["points"]

    embed = discord.Embed(
        title="🏡 YOUR SAFEHOUSE",
        description=(
            f"**{interaction.user.display_name}**, you made it out of the forest.\n\n"
            "The fireplace is warm. The door is locked behind you. "
            "For the first time since entering the forest... you're safe.\n\n"
            "🔥 **The fireplace is burning.**\n"
            "🛏️ **Your bed is waiting.**\n"
            "📚 **Your books are safe.**\n\n"
            "**You survived The Undead Forest.**"
        ),
        color=discord.Color.dark_green()
    )

    embed.add_field(
        name="🌲 Forest Status",
        value="**THE UNDEAD FOREST — SURVIVED**",
        inline=False
    )

    embed.add_field(
        name="🗺️ Locations Discovered",
        value="**8/8**",
        inline=True
    )

    embed.add_field(
        name="☣️ Survival Points",
        value=f"**{total_points}**",
        inline=True
    )

    await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# BONUS BOOK
# ============================================================

@bot.tree.command(
    name="bonus",
    description="Claim 50 points for an additional completed book."
)
@app_commands.describe(
    book="The additional completed book title"
)
async def bonus(
    interaction: discord.Interaction,
    book: str
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "☣️ Use this command inside a server.",
            ephemeral=True
        )

        return

    guild_id = interaction.guild.id
    user_id = interaction.user.id

    book = book.strip()

    if not book:

        await interaction.response.send_message(
            "⚠️ Please enter a book title.",
            ephemeral=True
        )

        return

    ensure_player(
        guild_id,
        user_id,
        interaction.user.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM bonus_books
        WHERE guild_id = ?
        AND user_id = ?
        AND LOWER(book_title) = LOWER(?)
    """, (
        guild_id,
        user_id,
        book
    ))

    existing = cursor.fetchone()

    if existing:

        connection.close()

        await interaction.response.send_message(
            "🔒 **BOOK ALREADY CLAIMED**\n\n"
            "You've already received bonus points for this book.",
            ephemeral=True
        )

        return

    cursor.execute("""
        INSERT INTO bonus_books
        (guild_id, user_id, book_title)
        VALUES (?, ?, ?)
    """, (
        guild_id,
        user_id,
        book
    ))

    cursor.execute("""
        UPDATE players
        SET points = points + ?
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        BONUS_BOOK_POINTS,
        guild_id,
        user_id
    ))

    connection.commit()

    cursor.execute("""
        SELECT points
        FROM players
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        guild_id,
        user_id
    ))

    total_points = cursor.fetchone()["points"]

    connection.close()

    embed = discord.Embed(
        title="⭐ BONUS BOOK SURVIVED!",
        description=(
            f"**{interaction.user.display_name}** "
            f"read beyond the required prompts."
        ),
        color=discord.Color.dark_green()
    )

    embed.add_field(
        name="📚 Book",
        value=book,
        inline=False
    )

    embed.add_field(
        name="⭐ Bonus",
        value=f"**+{BONUS_BOOK_POINTS} points**",
        inline=False
    )

    embed.add_field(
        name="☣️ Survival Points",
        value=f"**{total_points}**",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# LEADERBOARD
# ============================================================

@bot.tree.command(
    name="leaderboard",
    description="View the Undead Forest leaderboard."
)
async def leaderboard(
    interaction: discord.Interaction
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "☣️ Use this command inside a server.",
            ephemeral=True
        )

        return

    guild_id = interaction.guild.id

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT username, user_id, points
        FROM players
        WHERE guild_id = ?
        AND points > 0
        ORDER BY points DESC, username ASC
        LIMIT 10
    """, (
        guild_id,
    ))

    players = cursor.fetchall()

    connection.close()

    if not players:

        await interaction.response.send_message(
            "🪦 No survivors have earned points yet."
        )

        return

    medals = [
        "🥇",
        "🥈",
        "🥉"
    ]

    lines = []

    for index, player in enumerate(players):

        if index < 3:

            prefix = medals[index]

        else:

            prefix = f"**{index + 1}.**"

        lines.append(
            f"{prefix} **{player['username']}** — "
            f"**{player['points']} pts**"
        )

    embed = discord.Embed(
        title="🏆 UNDEAD FOREST LEADERBOARD",
        description="\n".join(lines),
        color=discord.Color.gold()
    )

    await interaction.response.send_message(
        embed=embed
    )


# ============================================================
# ADMIN: ADD POINTS
# ============================================================

@bot.tree.command(
    name="addpoints",
    description="Admin: add points to a survivor."
)
@app_commands.describe(
    member="Survivor",
    points="Points to add"
)
@app_commands.checks.has_permissions(
    manage_guild=True
)
async def addpoints(
    interaction: discord.Interaction,
    member: discord.Member,
    points: app_commands.Range[int, 1, 10000]
):

    guild_id = interaction.guild.id

    ensure_player(
        guild_id,
        member.id,
        member.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE players
        SET points = points + ?
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        points,
        guild_id,
        member.id
    ))

    connection.commit()
    connection.close()

    await interaction.response.send_message(
        f"🛠️ Added **+{points} points** to "
        f"**{member.display_name}**."
    )


# ============================================================
# ADMIN: REMOVE POINTS
# ============================================================

@bot.tree.command(
    name="removepoints",
    description="Admin: remove points from a survivor."
)
@app_commands.describe(
    member="Survivor",
    points="Points to remove"
)
@app_commands.checks.has_permissions(
    manage_guild=True
)
async def removepoints(
    interaction: discord.Interaction,
    member: discord.Member,
    points: app_commands.Range[int, 1, 10000]
):

    guild_id = interaction.guild.id

    ensure_player(
        guild_id,
        member.id,
        member.display_name
    )

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE players
        SET points = MAX(0, points - ?)
        WHERE guild_id = ?
        AND user_id = ?
    """, (
        points,
        guild_id,
        member.id
    ))

    connection.commit()
    connection.close()

    await interaction.response.send_message(
        f"🛠️ Removed **{points} points** from "
        f"**{member.display_name}**."
    )


# ============================================================
# START BOT
# ============================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN environment variable is missing."
    )

setup_database()

bot.run(TOKEN)
