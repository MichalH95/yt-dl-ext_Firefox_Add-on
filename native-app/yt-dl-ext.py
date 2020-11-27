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




# read a message from stdin and decode it
def get_message():
    raw_length = sys.stdin.buffer.read(4)

    if not raw_length:
        sys.exit(0)
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)


# encode a message for transmission, given its content
def encode_message(message_content):
    encoded_content = json.dumps(message_content).encode("utf-8")
    encoded_length = struct.pack('=I', len(encoded_content))
    return {'length': encoded_length, 'content': struct.pack(str(len(encoded_content))+"s",encoded_content)}


# send an encoded message to stdout
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


def update_youtube_dl():
    send_message("Updating youtube-dl")
    completedProcess = subprocess.run(["youtube-dl.exe", "-U"], capture_output=True, text=True)
    if not re.match("youtube-dl is up-to-date", completedProcess.stdout) and completedProcess.returncode != 0 :
        send_message("youtube-dl -U   failed, downloading youtube-dl manually")
        download_youtube_dl()
    send_message("Finished updating youtube-dl")


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


def download_videos(URLs, title):
    videoNum = 0;
    for videoURL in URLs:
        videoNum += 1;
        send_message("Starting video download " + str(videoNum) + " of " + str(len(URLs)))
        downloads_folder = os.path.expanduser("~/Downloads")
        output_template = downloads_folder + "/%(title)s-%(id)s.%(ext)s"

        completedProcess = subprocess.run(["youtube-dl", "-o", output_template, videoURL],
                                                        capture_output=True, text=True)

        if completedProcess.returncode != 0 :
            send_message("Download failed with error:\n" + completedProcess.stderr)
            send_message("Trying to update youtube-dl")
            update_youtube_dl()
            send_message("Retrying video download after updating youtube-dl")
            completedProcess = subprocess.run(["youtube-dl", "-o", output_template, videoURL],
                                                            capture_output=True, text=True)
            if completedProcess.returncode != 0 :
                send_message("Video download failed with error:\n" + completedProcess.stderr)

        send_message("Finished video download " + str(videoNum) + " of " + str(len(URLs)))
    send_message("Finished downloading " + title)
    send_message("^%Finished downloading " + title)


while True:
    msg = get_message()
    msglines = msg.splitlines()
    send_message("URLs received: " + msglines[0])
    title = msglines[1]
    URLs = msglines[2:]

    # if don't have youtube-dl, download it
    if not shutil.which("youtube-dl"):
        download_youtube_dl()

    # if don't have ffmpeg, download it
    if not shutil.which("ffmpeg"):
        if not Path("ffmpeg.zip").is_file():
            download_ffmpeg()
        extract_ffmpeg()

    # if don't have ffprobe, download it
    if not shutil.which("ffprobe"):
        if not Path("ffprobe.zip").is_file():
            download_ffprobe()
        extract_ffprobe()
    
    # download the videos
    download_videos(URLs, title)

