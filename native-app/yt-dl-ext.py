#!/usr/bin/python -u

import json
import sys
import struct
import requests
import subprocess
import re
import shutil
import io
import gdown
import os
from contextlib import redirect_stdout
from pathlib import Path
from pyunpack import Archive

# constants
youtube_dl_url = 'http://yt-dl.org/downloads/latest/youtube-dl.exe'
ffmpeg_url = 'https://drive.google.com/u/0/uc?id=1npG3IFATsS0kzThlRQRmwZbkO51edbFE'
ffprobe_url = 'https://drive.google.com/u/0/uc?id=1-1kYakHJn8SAzBxsX6DG9Ll-PP_06ZBG'





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
    r = requests.get(youtube_dl_url, allow_redirects=True)
    open('youtube-dl.exe', 'wb').write(r.content)
    send_message("Finished downloading youtube-dl")


# check if youtube-dl is updated and if not, update
def check_youtube_dl_version():
    send_message("Checking youtube-dl version")
    completedProcess = subprocess.run(["youtube-dl.exe", "-U"], capture_output=True, encoding="utf-8")
    if not re.match("youtube-dl is up-to-date", completedProcess.stdout):
        download_youtube_dl()
    send_message("Finished checking youtube-dl version")


def download_ffmpeg():
    send_message("Downloading ffmpeg")
    with redirect_stdout(io.StringIO()):
        gdown.download(ffmpeg_url, "ffmpeg.zip")
    send_message("Finished downloading ffmpeg")


def extract_ffmpeg():
    Archive("ffmpeg.zip").extractall(".")
    os.remove("ffmpeg.zip")

def download_ffprobe():
    send_message("Downloading ffprobe")
    with redirect_stdout(io.StringIO()):
        gdown.download(ffprobe_url, "ffprobe.zip")
    send_message("Finished downloading ffprobe")


def extract_ffprobe():
    Archive("ffprobe.zip").extractall(".")
    os.remove("ffprobe.zip")



while True:
    videoURL = get_message()
    send_message("URL received")

    # if don't have youtube-dl, download it
    if not shutil.which("youtube-dl"):
        download_youtube_dl()

    #if don't have ffmpeg, download it
    if not shutil.which("ffmpeg"):
        if not Path("ffmpeg.zip").is_file():
            download_ffmpeg()
        extract_ffmpeg()

    #if don't have ffprobe, download it
    if not shutil.which("ffprobe"):
        if not Path("ffprobe.zip").is_file():
            download_ffprobe()
        extract_ffprobe()
    
    # attempt to download the video
    send_message("Starting video download")
    #completedProcess = subprocess.run(["youtube-dl.exe", videoURL], capture_output=True, encoding="utf-8")
    #send_message(str(completedProcess))
    
    #check_youtube_dl_version()



