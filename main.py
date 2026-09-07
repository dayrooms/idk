import os
import websocket as ws
import discord
import requests
import sys
import json
from typing import Optional
import asyncio
import threading
from json import dumps
from colorama import Fore, init
import time

init(convert=True)

def Clear():
  if sys.platform in ["linux", "linux2"] or os.name == "posix":
    if not os.name == "nt":
      os.system("clear")
    else:
      os.system("cls")
  else:
    os.system('cls')

tokens = []
verify_tken = []
unchecked_tokens = []
session = requests.Session()
url = "https://discord.com/api/v10/users/@me"

def Check_Tokens(token):
  try:
    req = session.get(url=url, headers={"Authorization": token})
    if req.status_code in [204, 200, 201, 299]:
      if "need to verify" in req.text:
        print(f"ATM | {token[:20]}... Unverified Token.")
        verify_tken.append(token)
      else:
        print(f"ATM | {token[:20]}... Valid Token Added.")
        tokens.append(token)
    elif req.status_code in [499, 404, 401, 400]:
      print(f"ATM | {token[:20]}... Is Invalid Token And Removed From List.")
  except Exception as e:
    print(f"ATM | Error checking token {token[:20]}...: {e}")

# Load tokens from file
try:
  for token in open('tokens.txt', 'r').readlines():
    tk = token.strip()
    if tk:  # Only add non-empty tokens
      unchecked_tokens.append(tk)
except FileNotFoundError:
  print("ATM | tokens.txt file not found!")
  sys.exit(1)

print(f"ATM | Checking {len(unchecked_tokens)} tokens...")
for token in unchecked_tokens:
  Check_Tokens(token)

all_tkens = []
for token in verify_tken:
  all_tkens.append(token)
for tk in tokens:
  all_tkens.append(tk)

print(f"ATM | Total valid tokens: {len(all_tkens)}")

if len(all_tkens) == 0:
  print("ATM | No valid tokens found! Please check your tokens.txt file.")
  sys.exit(1)

with open('config.json') as config_file:
  nig = json.load(config_file)

status = nig["Status"]
st = status.lower()
activity = nig['Activity']
tyy = activity.lower()
name = nig['Activity_Name']
guild = nig['Guild_ID']
vc = nig['Voice_Channel_ID']

if st == "idle":
  ust = discord.Status.idle
elif st == "dnd":
  ust = discord.Status.dnd
elif st == "online":
  ust = discord.Status.online
else:
  ust = discord.Status.online

if tyy == "streaming":
  acttt = discord.Streaming(name=name, url="https://twitch.tv/teegrizzley")
elif tyy == "playing":
  acttt = discord.Game(name=name)
elif tyy == "listening":
  acttt = discord.Activity(type=discord.ActivityType.listening, name=name)
elif tyy == "watching":
  acttt = discord.Activity(type=discord.ActivityType.watching, name=name)
else:
  acttt = discord.Activity(type=discord.ActivityType.watching, name=name)

banner = f"""{Fore.RED}[-]{Fore.RESET} Created By ATM\n"""
print(banner)

async def join_voice_channel_proper(client, token):
  try:
    await client.wait_until_ready()
    print(f"ATM | Client ready for token: {token[:20]}...")

    guild_obj = client.get_guild(int(guild))
    if guild_obj:
      print(f"ATM | Found guild: {guild_obj.name}")
      voice_channel = guild_obj.get_channel(int(vc))
      if voice_channel:
        print(f"ATM | Found voice channel: {voice_channel.name}")

        # Send voice state update through the client's websocket
        await client.ws.send(dumps({
          "op": 4,
          "d": {
            "guild_id": str(guild),
            "channel_id": str(vc),
            "self_mute": True,
            "self_deaf": True
          }
        }))

        # Display success message with username and voice channel name
        username = f"{client.user.name}#{client.user.discriminator}" if client.user.discriminator != "0" else client.user.name
        print(f"ATM | {Fore.GREEN}[SUCCESS]{Fore.RESET} {username} successfully joined voice channel: {voice_channel.name}")
        return True
      else:
        print(f"ATM | Voice channel {vc} not found in guild")
    else:
      print(f"ATM | Guild {guild} not found")
    return False
  except Exception as e:
    print(f"ATM | Error joining voice channel for {token[:20]}...: {e}")
    return False

async def start_client_and_join(token, delay=0):
  try:
    # Add delay to stagger connections
    if delay > 0:
      await asyncio.sleep(delay)

    client = discord.Client(self_bot=True, status=ust, activity=acttt)

    @client.event
    async def on_ready():
      print(f"ATM | Client logged in as {client.user}")
      # Join voice channel using client's websocket connection
      await join_voice_channel_proper(client, token)

    @client.event
    async def on_error(event, *args, **kwargs):
      print(f"ATM | Discord error for {token[:20]}...: {event}")

    # Start the client
    await client.start(token, bot=False)
  except discord.LoginFailure:
    print(f"ATM | Login failed for token {token[:20]}... - Invalid token")
  except discord.HTTPException as e:
    print(f"ATM | HTTP error for token {token[:20]}...: {e}")
  except Exception as e:
    print(f"ATM | Error with token {token[:20]}...: {e}")

async def main():
  print(f"ATM | Starting {len(all_tkens)} tokens...")

  # Create tasks for all tokens with staggered delays
  tasks = []
  for i, tk in enumerate(all_tkens):
    # Add 3-5 second delay between each connection to avoid rate limits
    delay = i * 4
    task = asyncio.create_task(start_client_and_join(tk, delay))
    tasks.append(task)
    print(f"ATM | {tk[:20]}... scheduled to start in {delay} seconds.")

  print(f"ATM | All {len(tasks)} tokens scheduled. Waiting for connections...")

  # Wait for all tasks to complete
  await asyncio.gather(*tasks, return_exceptions=True)

# Run the main async function
if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    print("ATM | Bot stopped by user.")
  except Exception as e:
    print(f"ATM | Fatal error: {e}")
