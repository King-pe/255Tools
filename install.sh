#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python ffmpeg git
# Termux manages pip as a system package; never run "pip install --upgrade pip".
# --no-build-isolation avoids downloading build dependencies during installation.
python -m pip install --no-build-isolation --no-deps -e .
echo '255Tools installed successfully. Run: 255tools'
