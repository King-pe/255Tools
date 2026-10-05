#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python ffmpeg git
# No pip installation is needed. Termux manages pip as a system package.
# Install the standard-library CLI directly to the Termux command path.
install -Dm755 255tools/cli.py "$PREFIX/bin/255tools"
echo '255Tools installed successfully. Run: 255tools'
