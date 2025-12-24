from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# -------------------
# Discord bot setup
# -------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Configuration
# -------------------
ANNOUNCE_CHANNEL = "role-announcements"  # change to your public channel
WELCOME_CHANNEL = "welcome-channel"  # change to your welcome channel

# Custom messages per role
role_messages = {
    "omega": "{user} is now an omega, remember to take your suppressants!",
    "enigma": "Alphas LOOK OUT, {user} is an enigma, don't get too cocky *wink wink*",
    "beta": "Cool as a cucumber, {user} is our latest beta.",
    "alpha": "New CEO {user} is out to protect their Y/N!",
    "top": "Dick swinging, hide your asses, {user} is a top in town!",
    "bottom": "Don't get too tempted but {user} is a bottom!",
    "verse": "Jack of all trades, master of none, {user} is a verse!"
}

# Custom welcome message
def welcome_message(member):
    return f"Welcome our latest gooner {member.mention} to the server! Stay out the splash zone, *or don't*."

# -------------------
# Commands
# -------------------
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms", delete_after=5)

# -------------------
# Events
# -------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL)
    if channel:
        await channel.send(welcome_message(member))

@bot.event
async def on_member_update(before, after):
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    new_roles = after_roles - before_roles

    if new_roles:
        print(f"New roles detected for {after}: {[r.name for r in new_roles]}")
    
    for role in new_roles:
        print(f"Checking role: {role.name}")
        message_template = role_messages.get(role.name)
        if message_template:
            print(f"Found message template for {role.name}")
            channel = discord.utils.get(after.guild.text_channels, name=ANNOUNCE_CHANNEL)
            if channel:
                print(f"Sending message to {channel.name}")
                await channel.send(message_template.format(user=after.mention))
            else:
                print(f"Channel '{ANNOUNCE_CHANNEL}' not found!")
        else:
            print(f"No message template for role: {role.name}")

# -------------------
# Run bot
# -------------------
bot.run(os.getenv("DISCORD_TOKEN"))


