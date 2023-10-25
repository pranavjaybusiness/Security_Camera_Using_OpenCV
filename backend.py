
import config
import subprocess
from threading import Thread
import queue
import discord
import camera
import datetime

supported_backends = ["discord"]
incoming_messages = queue.Queue()
outgoing_messages = queue.Queue()


def initialize_backend():
    selected_backend = config.MessageBackend

    if selected_backend not in supported_backends:
        print(f"Error: Unknown backend! Defaulting to Discord backend! Given: {config.MessageBackend}")
        selected_backend = "discord"
        config.MessageBackend = "discord"

    if selected_backend == "discord":
        print("Backend callback: Initializing discord...")
        discord.init_discord()
    else:
        print("Backend not implemented!")

    backend_thread = Thread(target=process_messages)
    backend_thread.start()
    dispatch_message(["LoggingChannel", "Text", f"OpenCam started at {datetime.datetime.now()}"])


def dispatch_message(message_content):
    outgoing_messages.put(message_content)


def process_messages():
    while True:
        incoming_message = incoming_messages.get(block=True)

        if incoming_message.content == "df":
            disk_result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE)
            dispatch_message(["InputChannel", "text", f"```{str(disk_result.stdout)}```"])

        elif incoming_message.content == 'getmode':
            dispatch_message(["InputChannel", "Text", config.mode])

        elif incoming_message.content.startswith("setmode"):
            new_mode = incoming_message.content[7:].strip()
            if new_mode in ["auto", "enable", "disable"]:
                config.mode = new_mode
                dispatch_message(["InputChannel", "Text", f"Mode set to {config.mode}"])
            else:
                dispatch_message(["InputChannel", "Text", "Invalid! Valid options: auto, enable, disable"])

        elif incoming_message.content == 'getpic':
            print("Retrieving picture")
            dispatch_message(["InputChannel", "image", camera.capture_picture()])

        elif incoming_message.content == 'ping':
            dispatch_message(["InputChannel", "text", "pong"])
