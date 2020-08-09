#!/usr/bin/env python3
# Download non-watermarked TikTok videos
# Based on tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper)

import argparse
import json
import re
import requests
import sys
try:
    from tqdm import tqdm
except ImportError:
    print("could not load tqdm")
import io
from datetime import datetime


HEADERS = {
        "User-Agent": "x",
        }


def download(url, what=None):
    if what is not None:
        print(f"Downloading {what}...")

    r = requests.get(url, headers=HEADERS, stream=True)
    if not r.ok:
        print(f"could not download {what}")
        sys.exit(1)

    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024

    if 'tqdm' in sys.modules:
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
    f = io.BytesIO()
    for data in r.iter_content(block_size):
        if 'tqdm' in sys.modules:
            t.update(len(data))
        f.write(data)

    if 'tqdm' in sys.modules:
        t.close()

    f.seek(0)
    return f.read()

# parse program arguments
parser = argparse.ArgumentParser(description='Download TikTok videos without watermark')
parser.add_argument('url', nargs="?", type=str, help='TikTok url (ex. https://www.tiktok.com/@dreamcatcher_jp/video/6829190191849213186)')
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
content = download(url, what="webpage")
regex = r'<script id="__NEXT_DATA__" type="application/json" crossorigin="anonymous">(?P<json>.+?)</script>'
match = re.search(regex, content.decode())
if match is None:
    print("Could not find video")
    sys.exit(1)
video_url = json.loads(match.group('json'))['props']['pageProps']['videoData']['itemInfos']['video']['urls'][0]
print(video_url)

# get non-watermarked url
content = download(video_url, what="watermarked video")
vid_pos = content.find(b'vid:')
if vid_pos == -1:
    print("Could not extract vid")
    if output_file == None:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
        output = f"video_{dt_string}.mp4"
    else:
        output = output_file
    with open(output, "wb") as f:
        f.write(content)
    print(f"Watermarked(?) video written to {output}")
    sys.exit(1)
vid = content[vid_pos+4 : vid_pos + 36].decode("utf-8")

# download non-watermarked file
url = f"https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={vid}&h265=1&vr_type=0&is_play_url=1&source=PackSourceEnum_PUBLISH&media_type=4&"
content = download(url, what="non-watermarked video")
if output_file == None:
    output = f"{vid}.mp4"
else:
    output = output_file
with open(output, "wb") as f:
    f.write(content)
print(f"Downloaded video to {output}")
