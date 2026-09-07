import os
import json
import asyncio
import discord
with open("config.json", "r", encoding="utf-8") as f:
config = json.load(f)

GUILD_ID = int(config["Guild_ID"])
VOICE_CHANNEL_ID = int(config["Voice_Channel_ID"])

status_name = config.get("Status", "Online").lower()
activity_type = config.get("Activity", "Watching").lower()
activity_name = config.get("Activity_Name", "")

status_map = {
"online": discord.Status.online,
"idle": discord.Status.idle,
"dnd": discord.Status.dnd
}

status = status_map.get(status_name, discord.Status.online)

if activity_type == "playing":
activity = discord.Game(name=activity_name)
elif activity_type == "listening":
activity = discord.Activity(
type=discord.ActivityType.listening,
name=activity_name
)
elif activity_type == "watching":
activity = discord.Activity(
type=discord.ActivityType.watching,
name=activity_name
)
elif activity_type == "streaming":
activity = discord.Streaming(
name=activity_name,
url="https://www.twitch.tv/"
)
else:
activity = None

class VoiceBot(discord.Client):

async def on_ready(self):
    print(f"Logged in as {self.user}")

    guild = self.get_guild(GUILD_ID)

    if guild is None:
        print(f"ERROR: Could not find server {GUILD_ID}")
        return

    print(f"Found server: {guild.name}")

    channel = guild.get_channel(VOICE_CHANNEL_ID)

    if channel is None:
        print(f"ERROR: Could not find voice channel {VOICE_CHANNEL_ID}")
        return

    if not isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
        print("ERROR: Configured channel is not a voice channel.")
        return

    await self.join_voice(channel)

async def join_voice(self, channel):
    try:
        existing = discord.utils.get(
            self.voice_clients,
            guild=channel.guild
        )

        if existing and existing.is_connected():
            if existing.channel.id == channel.id:
                print(f"Already connected to: {channel.name}")
                return

            await existing.move_to(channel)
            print(f"Moved to: {channel.name}")
            return

        await channel.connect(
            self_mute=True,
            self_deaf=True
        )

        print(f"SUCCESS: Joined voice channel: {channel.name}")

    except Exception as e:
        print(f"Voice connection error: {e}")
        print("Retrying in 10 seconds...")

        await asyncio.sleep(10)

        await self.join_voice(channel)
intents = discord.Intents.default()
client = VoiceBot(
intents=intents,
status=status,
activity=activity
)

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
raise RuntimeError(
"DISCORD_TOKEN
