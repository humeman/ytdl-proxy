#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
    echo "error: run this as root"
    exit 1
fi


LOCATION=${LOCATION:-"/opt/ytdl-proxy"}
PORT=${PORT:-8200}

echo "Installing to ${LOCATION}"
mkdir -p "${LOCATION}"

echo "Getting yt-dlp"
git -C "${LOCATION}" clone https://github.com/yt-dlp/yt-dlp

echo "Copying ytdl-proxy"
cp -r . "${LOCATION}/ytdl-proxy"
mkdir "${LOCATION}/ytdl-proxy/out"

echo "Creating virtual environment"
python3 -m venv "${LOCATION}/venv"

echo "Installing requirements"
old_dir=$(pwd)
cd "${LOCATION}"
source "venv/bin/activate"
pip3 install -r ytdl-proxy/requirements.txt
cd yt-dlp
pip3 install .
cd ..

echo "Creating update service"

cat <<EOF > /etc/systemd/system/ytdl-proxy-update.service
[Unit]
Description=Update ytdl-proxy
After=network.target

[Service]
Type=oneshot
WorkingDirectory=${LOCATION}
ExecStart=${LOCATION}/ytdl-proxy/update.sh
EOF

cat <<EOF > /etc/systemd/system/ytdl-proxy-update.timer
[Unit]
Description=Daily update for ytdl-proxy and yt-dlp

[Timer]
OnCalendar=*-*-* 00:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo "Creating start service"

cat <<EOF > /etc/systemd/system/ytdl-proxy.service
[Unit]
Description=ytdl-proxy Service
After=network.target

[Service]
Type=simple
WorkingDirectory=${LOCATION}
ExecStart=${LOCATION}/ytdl-proxy/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting services"
systemctl daemon-reload
systemctl enable --now ytdl-proxy-update.timer
systemctl enable --now ytdl-proxy.service

cd "$old_dir"
echo "Done!"