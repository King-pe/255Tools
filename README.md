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

## Termux installation

```bash
pkg update -y
pkg install -y git
git clone https://github.com/King-pe/255Tools.git
cd 255Tools
bash install.sh
255tools
```

> **Termux note:** Do not run `pip install --upgrade pip`. Termux manages pip as a system package, and upgrading it is intentionally blocked. The included installer uses the Termux-compatible installation command.

## Responsible use

This is an educational project. Do not use it for phishing, spam, fake engagement, doxxing, account takeover, bypassing OTP/verification, or violating Terms of Service. The code is intentionally readable and beginner-friendly.
