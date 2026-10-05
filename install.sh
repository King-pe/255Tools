#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python ffmpeg git
python -m pip install --upgrade pip
python -m pip install -e .
echo '255Tools imewekwa. Endesha: 255tools'
