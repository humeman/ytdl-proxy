#!/bin/bash

set -e

source venv/bin/activate

cd yt-dlp
git pull
pip3 install .
cd ..
cd ytdl-proxy
git pull

systemctl restart ytdl-proxy.sh