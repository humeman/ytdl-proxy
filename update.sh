#!/bin/bash

set -e

source venv/bin/activate

cd yt-dlp
git clone
pip3 install .
cd ..
cd ytdl-proxy
git clone

systemctl restart ytdl-proxy.sh