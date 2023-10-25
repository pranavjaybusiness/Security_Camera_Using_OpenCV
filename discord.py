import discord
import os
from discord.ext import commands
import asyncio
import time
import datetime
from threading import Thread
import cv2
import imutils
import numpy as np
import json_parser
import config
import backend
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
print("ABOUT TO OVERWRITE TOKEN")
TOKEN = "0xDEADBEEF" # Secret, not in config file

config = dict()

# Discord main driver
# Whenever a three segment container is put into the output queue,
# this function, which is run on a separate thread, will pull it out
# and dispatch it to the discord backend
def discord_driver():
    time.sleep(5)
    print("Discord driver active")
    while(True):
        container = backend.outqueue.get(block=True)
        # Container should be [target, messagetype, message]
        channel = config[container[0]]
        if container[1] == "image":
            loc = container[2]
            chan = client.get_channel(channel)
            asyncio.run_coroutine_threadsafe(chan.send(file=discord.File(loc)),client.loop)
        else:
            chan = client.get_channel(channel)
            asyncio.run_coroutine_threadsafe(chan.send(container[2]), client.loop)

# Runs discord main loop
# Meant to be started on separate thread
def startdiscord():
    print("TOKEN="+TOKEN)
    client.run(TOKEN)


# Initializes the discord backend
# Loads the environment, fetches token, and starts threads
def init_discord():
    global TOKEN
    global config
    print("Loading dotenv")
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    print(TOKEN)
    config = json_parser.load_config("config/discord.json")
    print("Keys:" + str(config.keys()))
    # Start driver
    print("Starting discord driver")
    thread = Thread(target = discord_driver)
    thread.start()
    print("Starting discord.py")
    thread2 = Thread(target = startdiscord)
    thread2.start()
    print("Done")

@client.event
async def on_readt():
    print("OpenCAM Backend initialized: Discord connected")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Only take commands from that specific channel
    print(message.channel.id)
    if(message.channel.id == config["InputChannel"]):
        print(message.content)
        backend.inqueue.put(message) # message just came in, let's record it
        # Queue is thread safe, so no worries there