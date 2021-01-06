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
import shlex
from contextlib import redirect_stdout
from pathlib import Path
from pyunpack import Archive


# constants
youtube_dl_url = 'http://yt-dl.org/downloads/latest/youtube-dl.exe'
ffmpeg_url = 'https://drive.google.com/u/0/uc?id=1npG3IFATsS0kzThlRQRmwZbkO51edbFE'
ffprobe_url = 'https://drive.google.com/u/0/uc?id=1-1kYakHJn8SAzBxsX6DG9Ll-PP_06ZBG'

# extra command-line arguments
videoargs = []
musicargs = []
podcastargs = []
globalargs = []


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
    global youtube_dl_url
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
    global ffmpeg_url
    send_message("Downloading ffmpeg")
    with redirect_stdout(io.StringIO()):
        gdown.download(ffmpeg_url, "ffmpeg.zip")
    send_message("Finished downloading ffmpeg")


def extract_ffmpeg():
    Archive("ffmpeg.zip").extractall(".")
    os.remove("ffmpeg.zip")


def download_ffprobe():
    global ffprobe_url
    send_message("Downloading ffprobe")
    with redirect_stdout(io.StringIO()):
        gdown.download(ffprobe_url, "ffprobe.zip")
    send_message("Finished downloading ffprobe")


def extract_ffprobe():
    Archive("ffprobe.zip").extractall(".")
    os.remove("ffprobe.zip")


def download_videos(URLs, title):
    videosCount = len(URLs);
    videosCountStr = str(len(URLs));
    videoNum = 0;
    updated = False;
    failedCnt = 0;
    for videoURL in URLs:
        videoNum += 1;
        send_message("  Starting video download " + str(videoNum) + " of " + videosCountStr)
        downloads_folder = os.path.expanduser("~/Downloads")
        output_template = downloads_folder + "/yt-dl-ext downloads/%(title)s-%(id)s.%(ext)s"
        vidtitle = get_video_title(videoURL)
        category = nn_predict_video_category(vidtitle)
        extra_args_array = get_extra_args_array(category)
        ytdlargs = ["youtube-dl", "-o", output_template]
        ytdlargs.extend(extra_args_array)
        ytdlargs.extend(globalargs)
        ytdlargs.append(videoURL)
        print("youtube-dl args: " + str(ytdlargs), file=sys.stderr)
        completedProcess = subprocess.run(ytdlargs, capture_output=True, text=True)

        if completedProcess.returncode != 0 :
            send_message("      Download failed with error:\n" + completedProcess.stderr)
            if not updated :
                send_message("      Trying to update youtube-dl")
                update_youtube_dl()
                updated = True;
                send_message("      Retrying video download after updating youtube-dl")
                completedProcess = subprocess.run(ytdlargs, capture_output=True, text=True)
                if completedProcess.returncode != 0 :
                    send_message("      Download after update failed with error:\n" + completedProcess.stderr)
                    failedCnt += 1;
                    send_message("  Download failed of video " + str(videoNum) + " of " + videosCountStr)
                    continue
            else :
                failedCnt += 1;
                send_message("  Download failed of video " + str(videoNum) + " of " + videosCountStr)
                continue

        send_message("  Finished download video " + str(videoNum) + " of " + videosCountStr)
    if failedCnt > 0 :
        if videosCount > 1 :
            send_message("Failed downloading " + str(failedCnt) + " of " + videosCountStr + " videos")
            send_message("^%Failed downloading " + str(failedCnt) + " of " + videosCountStr + " videos")
        else :
            send_message("Failed downloading " + title)
            send_message("^%Failed downloading " + title)
    else :
        send_message("Finished downloading " + title)
        send_message("^%Finished downloading " + title)


def process_cmdlargs_change(changes):
    global videoargs
    global musicargs
    global podcastargs
    global globalargs
    for i in range(0, int(len(changes)/2)) :
        idx = i*2;
        category = changes[idx]
        if category == "video" :
            videoargs = shlex.split(changes[idx+1])
        elif category == "music" :
            musicargs = shlex.split(changes[idx+1])
        elif category == "podcast" :
            podcastargs = shlex.split(changes[idx+1])
        elif category == "global" :
            globalargs = shlex.split(changes[idx+1])


def get_video_title(videoURL):
    ytdlargs = ["youtube-dl", "--get-title", videoURL]
    completedProcess = subprocess.run(ytdlargs, capture_output=True, text=True)
    return completedProcess.stdout


def nn_predict_video_category(vidtitle):
    # predict and get video category from neural network
    return "video"


def get_extra_args_array(category):
    if category == "video" :
        return videoargs
    elif category == "music" :
        return musicargs
    elif category == "podcast" :
        return podcastargs


while True:
    msg = get_message()
    msglines = msg.splitlines()
    
    # special messages begin with ^% on first line
    first_line = msglines[0]
    if first_line[0:2] == '^%' :
        first_line = first_line[2:]
        if first_line == 'Extra command-line arguments change' :
            changes = msglines[1:]
            process_cmdlargs_change(changes)
    else :
    # received video URLs
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

