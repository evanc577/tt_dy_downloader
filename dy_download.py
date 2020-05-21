#!/usr/bin/env python3
# Download non-watermarked TikTok videos
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
parser.add_argument('url', type=str, help='TikTok url (ex. https://www.tiktok.com/@dreamcatcher_jp/video/6829190191849213186)')
parser.add_argument('-o', '--output', type=str, help='output video filename')
args = parser.parse_args()

resp = requests.get(args.url, headers=HEADERS)

# find video url (watermarked)
regex = r'playAddr: "(?P<url>.+?)"'
match = re.search(regex, resp.text)
video_url = match.group('url')

# get non-watermarked url
vid_pos = -1
for i in range(10):
    print(f"attempt {i+1}")
    resp = requests.get(video_url, headers=HEADERS)
    vid_pos = resp.content.find(b'vid:')
    if vid_pos != -1:
        break
if vid_pos == -1:
    sys.exit(1)
vid = resp.content[vid_pos+4 : vid_pos+36].decode("utf-8")

# download non-watermarked file
resp = requests.get(f"https://aweme.snssdk.com/aweme/v1/play/?video_id={vid}&improve_bitrate=1&ratio=1080p", headers=HEADERS)
if args.output == None:
    output = f"{vid}.mp4"
else:
    output = args.output
with open(output, "wb") as f:
    f.write(resp.content)
print(f"Downloaded to {output}")
