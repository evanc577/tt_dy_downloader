#!/usr/bin/env python3
# Download non-watermarked TikTok videos
# Based on tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper)

import argparse
import json
import re
import requests

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.1",
        }

# parse program arguments
parser = argparse.ArgumentParser(description='Download TikTok videos without watermark')
parser.add_argument('url', type=str, help='TikTok url (ex. https://www.tiktok.com/@dreamcatcher_jp/video/6829190191849213186)')
parser.add_argument('-o', '--output', type=str, help='output video filename')
args = parser.parse_args()

resp = requests.get(args.url, headers=HEADERS)

# find video url (watermarked)
regex = r'<script id="__NEXT_DATA__" type="application/json" crossorigin="anonymous">(?P<json>.+?)</script>'
match = re.search(regex,resp.text)
video_url = json.loads(match.group('json'))['props']['pageProps']['videoData']['itemInfos']['video']['urls'][0]

# get non-watermarked url
resp = requests.get(video_url, headers=HEADERS)
vid_pos = resp.content.find(b'vid:')
video_id = resp.content[vid_pos+4 : vid_pos + 36].decode("utf-8")

# download non-watermarked file
resp = requests.get(f"https://api2.musical.ly/aweme/v1/playwm/?video_id={video_id}&improve_bitrate=1&ratio=1080p", headers=HEADERS)
if args.output == None:
    output = f"{video_id}.mp4"
else:
    output = args.output
with open(output, "wb") as f:
    f.write(resp.content)
print(f"Downloaded to {output}")
