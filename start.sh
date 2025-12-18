#!/bin/bash

source venv/bin/activate
cd ytdl-proxy
hypercorn ytdl_proxy:app \
    --bind 0.0.0.0:${PORT:8200} \
    --workers 1