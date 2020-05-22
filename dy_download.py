#!/usr/bin/env python3
# Download non-watermarked Douyin videos
# Based on tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper)

import argparse
import json
import re
import requests
import sys

HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
        }

# parse program arguments
parser = argparse.ArgumentParser(description='Download TikTok videos without watermark')
parser.add_argument('url', nargs="?", type=str, help='Douyin url (ex. https://v.douyin.com/J166N8y/)')
parser.add_argument('-o', '--output', type=str, help='output video filename')
args = parser.parse_args()

# get url
if args.url is not None:
    user_url = args.url
else:
    user_url = input("URL: ")

# parse url
url_regex = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
match = re.search(url_regex, user_url)
if match is None:
    print("Invalid URL")
    sys.exit(1)
url = match.group()

# get output file
if args.output is not None:
    output_file = args.output
else:
    output_file = input("Output name (blank for default): ")
    if output_file == "":
        output_file = None

# find video url (watermarked)
resp = requests.get(url, headers=HEADERS)
regex = r'playAddr: "(?P<url>.+?)"'
match = re.search(regex, resp.text)
if match is None:
    print("Could not download video")
    sys.exit(1)
video_url = match.group('url')

# get non-watermarked url
vid_pos = -1
resp = requests.get(video_url, headers=HEADERS)
vid_pos = resp.content.find(b'vid:')
if vid_pos == -1:
    print("Could not extract vid")
    sys.exit(1)
vid = resp.content[vid_pos+4 : vid_pos+36].decode("utf-8")

# download non-watermarked file
resp = requests.get(f"https://aweme.snssdk.com/aweme/v1/play/?video_id={vid}&improve_bitrate=1&ratio=1080p", headers=HEADERS)
if not resp.ok or len(resp.content) == 0:
    print("Could not download no watermark video")
    sys.exit(1)
if output_file == None:
    output = f"{vid}.mp4"
else:
    output = output_file
with open(output, "wb") as f:
    f.write(resp.content)
print(f"Downloaded to {output}")
