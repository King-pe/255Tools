# 255Tools

**255Tools** is a green/blue Termux toolkit for learning Python, APIs, safe networking, and legitimate command-line usage.

## Features

1. **Domain checker** — uses RDAP to show whether a domain has registration information.
2. **Temp mail demo** — connects to mail.tm for legitimate inbox testing; do not use it for spam, bypasses, or fake accounts.
3. **YouTube Growth Audit** — provides channel growth recommendations; it does not add fake subscribers/followers. Use YouTube Studio/vidIQ for analytics while logged in yourself.
4. **Video downloader** — a `yt-dlp` wrapper for videos you are authorized to save. It targets approximately 250p when available.
5. **Public username finder** — checks public profile links only; it does not search for phone numbers, email addresses, locations, or private data.
6. **Developer** — information about MrCodex1Tz.

> **MVP note:** Temp mail currently includes a demo for creating an inbox through mail.tm; login, inbox reading, and sending messages require session/token handling planned for a future version. The growth feature is an audit only—no fake subscribers are added.

### Optional vidIQ configuration

The CLI reads the credential from the current Termux environment and never stores it in the repository:

```bash
export VIDIQ_API_KEY="your-rotated-vidiq-key"
255tools
```

Alternatively, create a private environment file. The `.env` file contains a value, not Python code:

```bash
mkdir -p ~/.255tools
cp .env.example ~/.255tools/.env
```

Edit `~/.255tools/.env` so it contains only:

```text
VIDIQ_API_KEY=your-rotated-vidiq-key
```

The CLI reads this file automatically. `.env` is ignored by Git and must never be committed.

### Optional Vercel vidIQ backend

For live vidIQ analytics, 255Tools now uses your deployed backend by default:

`https://255tools-backed.vercel.app`

Set `VIDIQ_API_KEY` and `BACKEND_TOKEN` in Vercel Environment Variables, then add the backend token to `~/.255tools/.env`:

```text
VIDIQ_BACKEND_URL=https://255tools-backed.vercel.app
VIDIQ_BACKEND_TOKEN=the-same-backend-token
```

The CLI sends only the channel URL and backend token. The vidIQ key stays inside Vercel and is never sent to Termux or GitHub.

If Growth Audit reports `401`, set the exact same random value in both places:

- Vercel: `BACKEND_TOKEN`
- Termux: `VIDIQ_BACKEND_TOKEN`

After changing the CLI, update the installed command with `cd ~/255Tools && git pull && bash install.sh`.

Do not paste a real key into `cli.py`, `README.md`, or GitHub. Because a key was shared in chat, revoke or rotate it in vidIQ before using the replacement. Live analytics still require an official vidIQ API/MCP endpoint and an authorized account.

## Termux installation

```bash
pkg update -y
pkg install -y git
git clone https://github.com/King-pe/255Tools.git
cd 255Tools
bash install.sh
255tools
```

> **Termux note:** No pip installation is required. Do not run `pip install --upgrade pip`; Termux manages pip as a system package, and upgrading it is intentionally blocked. The included installer places the CLI directly in `$PREFIX/bin`.

The downloader automatically sanitizes and trims long social-media titles so Facebook/Reels filenames do not exceed the Linux/Termux filename limit. To update an existing installation, run `git pull && bash install.sh`.

## Responsible use

This is an educational project. Do not use it for phishing, spam, fake engagement, doxxing, account takeover, bypassing OTP/verification, or violating Terms of Service. The code is intentionally readable and beginner-friendly.
