# 255Tools

**255Tools** is a green/blue Termux toolkit for learning Python, APIs, safe networking, and legitimate command-line usage.

## Features

1. **Domain checker** — uses RDAP to show whether a domain has registration information.
2. **Temp mail account** — creates or logs into an inbox you control through mail.tm, lists messages, reads a selected message, and sends email; do not use it for spam, bypasses, or fake accounts.
3. **Video downloader** — a `yt-dlp` wrapper for videos you are authorized to save. It targets approximately 250p when available.
4. **Social lookup** — checks GitHub, YouTube, Facebook, Instagram, X/Twitter, and TikTok public profile links only; it does not search for phone numbers, email addresses, locations, private data, or private accounts.
5. **Domain DNS Check** — checks A/AAAA addresses and, when `dig` is installed, NS/MX/TXT records to help verify DNS configuration.
6. **My IP** — shows your public IP, country, region, city, ISP, ASN, timezone, latitude and longitude.
7. **IP Lookup** — looks up the same public metadata for an IP address you enter.
8. **Port Scanner** — performs a bounded TCP connect scan against common ports or a user-provided list/range of up to 100 ports.
9. **Wi-Fi Scanner** — lists nearby SSIDs and signal/security information through Termux:API; it can request a connection to a network you are authorized to use with a hidden password prompt.
10. **Internet Speed** — measures approximate download Mbps and HTTP latency using a limited public sample.
11. **DNS Server Links** — prints Android Private DNS hostnames and DNS-over-HTTPS links for AdGuard (ads/trackers), Cloudflare (speed), and Quad9 (malware blocking).
12. **HTTP Headers & SSL Check** — inspects response status/headers and validates the TLS certificate subject, issuer, protocol, expiry, and remaining days.
13. **Developer** — information about MrCodex1Tz.

> **MVP note:** YouTube Boost/Growth Audit has been removed; 255Tools does not add fake subscribers. SMS sending is not included: use a legitimate SMS provider and the recipient's consent for messaging.

IP location is approximate provider-level geolocation. It does not reveal a reliable person identity or exact street address.

Port Scanner is for systems you own or have explicit permission to test. It uses a short timeout, reports open TCP ports only, and limits each scan to 100 ports.

Wi-Fi scanning requires the separate **Termux:API Android app**, Android location permission, and the `termux-api` package. The tool does not brute-force passwords, capture other users' credentials, or connect to networks without authorization.

DNS links do not create a private DNS server or guarantee faster internet; performance depends on the carrier and location. AdGuard blocks many ads and trackers, but no DNS service blocks every ad. Choose the provider in Android **Private DNS** settings and switch back if an app or website needs another resolver.

HTTP security checks redact cookies and authorization headers so session secrets are not printed to the terminal.

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
