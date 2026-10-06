# 255Tools

**255Tools** is a green/blue Termux toolkit for learning Python, APIs, safe networking, and legitimate command-line usage.

## Features

1. **Domain checker** — uses RDAP to show whether a domain has registration information.
2. **Temp mail demo** — connects to mail.tm for legitimate inbox testing; do not use it for spam, bypasses, or fake accounts.
3. **Video downloader** — a `yt-dlp` wrapper for videos you are authorized to save. It targets approximately 250p when available.
4. **Public username finder** — checks GitHub, YouTube, Facebook, Instagram, X, and TikTok public profile links only; it does not search for phone numbers, email addresses, locations, or private data.
5. **Domain DNS Check** — checks A/AAAA addresses and, when `dig` is installed, NS/MX/TXT records to help verify DNS configuration.
6. **Developer** — information about MrCodex1Tz.

> **MVP note:** Temp mail currently includes a demo for creating an inbox through mail.tm; login, inbox reading, and sending messages require session/token handling planned for a future version. YouTube Boost/Growth Audit has been removed; 255Tools does not add fake subscribers.

## Termux installation

```bash
pkg update -y
pkg install -y git dnsutils
git clone https://github.com/King-pe/255Tools.git
cd 255Tools
bash install.sh
255tools
```

> **Termux note:** No pip installation is required. Do not run `pip install --upgrade pip`; Termux manages pip as a system package, and upgrading it is intentionally blocked. The included installer places the CLI directly in `$PREFIX/bin`.

The downloader automatically sanitizes and trims long social-media titles so Facebook/Reels filenames do not exceed the Linux/Termux filename limit. To update an existing installation, run `git pull && bash install.sh`.

## Responsible use

This is an educational project. Do not use it for phishing, spam, fake engagement, doxxing, account takeover, bypassing OTP/verification, or violating Terms of Service. The code is intentionally readable and beginner-friendly.
