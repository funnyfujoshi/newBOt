# ------------------- CLEAN DISCORD BOT WITH SIMPLE LOGGING -------------------
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands, tasks
from collections import deque
from datetime import datetime
import logging

# ------------------- ENVIRONMENT -------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ANNOUNCE_CHANNEL_ID = int(os.getenv("ANNOUNCE_CHANNEL_ID", 0))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 0))

if not DISCORD_TOKEN or not ANNOUNCE_CHANNEL_ID or not WELCOME_CHANNEL_ID:
    raise RuntimeError("Check your .env: missing token or channel IDs.")

# ------------------- LOGGING -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
logging.getLogger("discord").setLevel(logging.WARNING)

# ------------------- DISCORD BOT -------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Fixed: needed for commands to work
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- STATE -------------------
role_messages = {
    "omega": "{user} is now an omega, remember to take your suppressants!",
    "enigma": "Alphas LOOK OUT, {user} is an enigma, don't get too cocky *wink wink*",
    "beta": "Cool as a cucumber, unbothered by pheremones, {user} is our latest beta.",
    "alpha": "New CEO {user} is out to protect their Y/N!",
    "top": "Dick swinging, hide your asses, {user} is a top in town!",
    "bottom": "Don't get too tempted but {user} is a bottom!",
    "verse": "Jack of all trades, master of none, {user} is a verse!"
}

DEFAULT_ROLE_MESSAGE = "*OOOOOOOOO* {user} just got the **{roles}** role(s)"

recent_joins = deque(maxlen=50)
recent_role_changes = deque(maxlen=50)

# ------------------- HELPERS -------------------
async def safe_send(channel, message):
    if channel:
        try:
            await channel.send(message)
            logging.info(f"Sent message to {channel.name}: {message}")
        except discord.DiscordException as e:
            logging.warning(f"Failed to send message: {e}")

# ------------------- EVENTS -------------------
@bot.event
async def on_ready():
    logging.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    heartbeat.start()

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    message = f"Welcome our latest gooner {member.mention} to the server! Stay out the splash zone, or don't."
    await safe_send(channel, message)
    recent_joins.appendleft({"member": member.name, "message": message, "timestamp": datetime.utcnow().isoformat()})
    logging.info(f"{member.name} joined.")

@bot.event
async def on_member_update(before, after):
    new_roles = [r for r in after.roles if r not in before.roles and r.name != "@everyone"]
    if not new_roles:
        return
    channel = after.guild.get_channel(ANNOUNCE_CHANNEL_ID)
    for role in new_roles:
        template = role_messages.get(role.name.lower())
        msg = template.format(user=after.mention) if template else DEFAULT_ROLE_MESSAGE.format(user=after.mention, roles=role.name)
        await safe_send(channel, msg)
        recent_role_changes.appendleft({"member": after.name, "role": role.name, "message": msg, "timestamp": datetime.utcnow().isoformat()})
        logging.info(f"{after.name} got role {role.name}.")

# ------------------- COMMANDS -------------------
@bot.command()
async def ping(ctx):
    """Better ping command: shows websocket + message latency."""
    before = discord.utils.utcnow()
    message = await ctx.send("Pinging...")
    after = discord.utils.utcnow()
    
    ws_latency = round(bot.latency * 1000)
    msg_latency = round((after - before).total_seconds() * 1000)
    
    await message.edit(content=f"Pong! 🏓\nWebSocket Latency: {ws_latency}ms\nMessage Roundtrip: {msg_latency}ms")

@bot.command()
async def set_announce(ctx, channel: discord.TextChannel):
    global ANNOUNCE_CHANNEL_ID
    ANNOUNCE_CHANNEL_ID = channel.id
    await ctx.send(f"Announcement channel set to {channel.mention}")
    logging.info(f"Announcement channel changed to {channel.name} ({channel.id})")

@bot.command()
async def set_welcome(ctx, channel: discord.TextChannel):
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    await ctx.send(f"Welcome channel set to {channel.mention}")
    logging.info(f"Welcome channel changed to {channel.name} ({channel.id})")

@bot.command()
async def add_role_message(ctx, role_name: str, *, message: str):
    role_messages[role_name.lower()] = message
    await ctx.send(f"Added/updated role message for `{role_name}`.")
    logging.info(f"Role message added/updated for {role_name}")

@bot.command()
async def remove_role_message(ctx, role_name: str):
    if role_name.lower() in role_messages:
        del role_messages[role_name.lower()]
        await ctx.send(f"Removed role message for `{role_name}`.")
        logging.info(f"Role message removed for {role_name}")
    else:
        await ctx.send(f"No message found for `{role_name}`.")

# ------------------- HEARTBEAT -------------------
@tasks.loop(minutes=5)
async def heartbeat():
    logging.info("Bot heartbeat alive")

# ------------------- RUN BOT -------------------
bot.run(DISCORD_TOKEN)



