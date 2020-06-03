#!/usr/bin/env python3
# Download non-watermarked TikTok videos
# Based on tiktok-scraper (https://github.com/drawrowfly/tiktok-scraper)

import argparse
import json
import re
import requests
import sys
from tqdm import tqdm
import io


HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.1",
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

    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    f = io.BytesIO()
    for data in r.iter_content(block_size):
        t.update(len(data))
        f.write(data)
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

# get non-watermarked url
content = download(video_url, what="watermarked video")
vid_pos = content.find(b'vid:')
if vid_pos == -1:
    print("Could not extract vid")
    sys.exit(1)
vid = content[vid_pos+4 : vid_pos + 36].decode("utf-8")

# download non-watermarked file
content = download(f"https://api2.musical.ly/aweme/v1/playwm/?video_id={vid}&improve_bitrate=1&ratio=1080p", what="non-watermarked video")
if output_file == None:
    output = f"{vid}.mp4"
else:
    output = output_file
with open(output, "wb") as f:
    f.write(content)
print(f"Downloaded video to {output}")
