#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python ffmpeg git dnsutils termux-api
# No pip installation is needed. Termux manages pip as a system package.
# Install a small launcher that always runs the current repository source.
# This prevents `$PREFIX/bin/255tools` from becoming a stale copied version.
REPO_DIR="$(pwd)"
if [ ! -f "$REPO_DIR/255tools/cli.py" ]; then
  echo "Run this installer from the 255Tools repository directory."
  exit 1
fi
cat > "$PREFIX/bin/255tools" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec python3 "$REPO_DIR/255tools/cli.py" "\$@"
EOF
chmod 755 "$PREFIX/bin/255tools"
echo "255Tools installed successfully from: $REPO_DIR"
echo 'Future updates: cd into the repo, run git pull, then run 255tools.'
