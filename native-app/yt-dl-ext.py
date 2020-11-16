#!/usr/bin/python -u

import json
import sys
import struct
import requests
import subprocess
from pathlib import Path
import re


# read a message from stdin and decode it.
def get_message():
    raw_length = sys.stdin.buffer.read(4)

    if not raw_length:
        sys.exit(0)
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)


# encode a message for transmission, given its content.
def encode_message(message_content):
    encoded_content = json.dumps(message_content).encode("utf-8")
    encoded_length = struct.pack('=I', len(encoded_content))
    return {'length': encoded_length, 'content': struct.pack(str(len(encoded_content))+"s",encoded_content)}


# send an encoded message to stdout.
def send_message(message):
    encoded_message = encode_message(message)
    sys.stdout.buffer.write(encoded_message['length'])
    sys.stdout.buffer.write(encoded_message['content'])
    sys.stdout.buffer.flush()


# download youtube-dl.exe to current directory
def download_youtube_dl():
    send_message("Downloading youtube-dl")
    ytdlurl = 'http://yt-dl.org/downloads/latest/youtube-dl.exe'
    r = requests.get(ytdlurl, allow_redirects=True)
    open('youtube-dl.exe', 'wb').write(r.content)
    send_message("Finished downloading youtube-dl")


def check_youtube_dl_version():
    send_message("Checking youtube-dl version")
    completedProcess = subprocess.run(["youtube-dl.exe", "-U"], capture_output=True, encoding="utf-8")
    if re.match("youtube-dl is up-to-date", completedProcess.stdout) == None:
        download_youtube_dl()
    #send_message(str(completedProcess))
    send_message("Finished checking youtube-dl version")



while True:
    message = get_message()
    send_message("URL received")

    # if don't have youtube-dl, download it
    if not Path("youtube-dl.exe").is_file():
        download_youtube_dl()

    

