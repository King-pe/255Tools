#!/usr/bin/env python3
"""255Tools: safe, educational Termux utilities."""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

G = '\033[92m'; B = '\033[94m'; C = '\033[96m'; Y = '\033[93m'; R = '\033[91m'; X = '\033[0m'


def load_env_file():
    """Load simple KEY=VALUE entries without overwriting real environment vars."""
    candidates = [Path.cwd() / '.env', Path.home() / '.255tools' / '.env']
    for env_file in candidates:
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()
BANNER = r'''██████╗ ███████╗███████╗████████╗ ██████╗  ██████╗ ██╗     ███████╗
╚════██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║     ██╔════╝
 █████╔╝███████╗███████╗   ██║   ██║  ██║██║  ██║██║     ███████╗
██╔═══╝ ╚════██║╚════██║   ██║   ██║  ██║██║  ██║██║     ╚════██║
███████╗███████║███████║   ██║   ╚█████╔╝╚█████╔╝███████╗███████║
╚══════╝╚══════╝╚══════╝   ╚═╝    ╚════╝  ╚════╝ ╚══════╝╚══════╝'''


def get(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': '255Tools/1.0 educational-cli', **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', errors='replace'), r.headers.get_content_type()


def ask(label):
    try: return input(f'{C}{label}{X} ').strip()
    except (EOFError, KeyboardInterrupt): print(); return ''


def domain_check():
    domain = ask('Enter domain (example.com):').lower().strip()
    domain = re.sub(r'^https?://', '', domain).split('/')[0]
    if not re.match(r'^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$', domain):
        print(f'{R}Invalid domain.{X}'); return
    try:
        data, _ = get(f'https://rdap.org/domain/{urllib.parse.quote(domain)}')
        obj = json.loads(data)
        status = ', '.join(obj.get('status', [])) or 'unknown'
        print(f'{G}The domain appears to be registered / information is available.{X}')
        print(f'  Domain: {domain}\n  Status: {status}')
    except urllib.error.HTTPError as e:
        if e.code == 404: print(f'{G}The domain appears to be unregistered (available candidate).{X}')
        else: print(f'{Y}RDAP returned HTTP {e.code}; jaribu tena baadaye.{X}')
    except Exception as e: print(f'{Y}Could not verify live: {e}{X}')


def temp_mail():
    print(f'{Y}Educational use only: use this inbox for legitimate testing, not spam, bypasses, or fake accounts.{X}')
    print('1) Create temporary inbox  2) Check inbox  3) Send message')
    choice = ask('Choose:')
    if choice == '1':
        try:
            domains = json.loads(get('https://api.mail.tm/domains')[0])['hydra:member']
            domain = domains[0]['domain']; username = ask('New username:') or f'user{os.getpid()}'
            address = f'{username}@{domain}'; password = ask('Password (visible while typing):')
            payload = json.dumps({'address': address, 'password': password}).encode()
            req = urllib.request.Request('https://api.mail.tm/accounts', data=payload, headers={'Content-Type':'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=15) as r:
                created = json.loads(r.read())
                print(f"{G}Inbox created: {created.get('address', address)}{X}")
            print(f'{Y}Save the address and password for later use.{X}')
        except Exception as e: print(f'{R}Mail.tm error: {e}{X}')
    elif choice in ('2','3'):
        print(f'{Y}For safety, login/token management is left for the tutorial. Use the mail.tm API docs and do not use it for spam.{X}')
    else: print('Invalid choice.')


def youtube_audit():
    url = ask('Paste channel URL:')
    if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', url): print(f'{R}Invalid YouTube URL.{X}'); return
    print(f'{G}Educational Growth Audit:{X}')
    backend = os.environ.get('VIDIQ_BACKEND_URL', '').rstrip('/')
    if backend:
        try:
            payload = json.dumps({'channel_url': url}).encode()
            headers = {'Content-Type': 'application/json'}
            if os.environ.get('VIDIQ_BACKEND_TOKEN'):
                headers['Authorization'] = f"Bearer {os.environ['VIDIQ_BACKEND_TOKEN']}"
            req = urllib.request.Request(f'{backend}/growth-audit', data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
            print(f'{G}Live vidIQ backend audit received.{X}')
            print(json.dumps(result.get('result', result), indent=2, ensure_ascii=False))
            return
        except Exception as error:
            print(f'{Y}Backend audit unavailable: {error}{X}')
    if os.environ.get('VIDIQ_API_KEY'):
        print(f'{G}vidIQ API key detected from the environment.{X}')
    else:
        print(f'{Y}vidIQ API key not configured. Set VIDIQ_API_KEY in your Termux session.{X}')
    print('• No fake followers/subscribers are added.')
    print('• Improve your title, thumbnail, retention, consistency, and SEO.')
    print('• For live vidIQ analytics, use an official vidIQ API/MCP endpoint with your authorized account.')
    print(f'{B}Channel URL: {url}{X}')


def download_video():
    url = ask('Paste video URL:')
    if not url.startswith(('http://','https://')): print(f'{R}Invalid URL.{X}'); return
    if not shutil.which('yt-dlp'):
        print(f'{Y}yt-dlp is not installed. Install it with: pkg update && pkg install python ffmpeg && pip install -U yt-dlp{X}'); return
    print(f'{Y}Download only videos you are allowed to save; respect copyright and the Terms of Service.{X}')
    out = ask('Folder [downloads]:') or 'downloads'; Path(out).mkdir(exist_ok=True)
    # Facebook and other platforms can return extremely long titles. Keep the
    # saved filename portable for Termux/Linux filesystems.
    cmd = ['yt-dlp','--restrict-filenames','--trim-filenames','120',
           '-f','bv*[height<=250]+ba/b[height<=250]/best',
           '-o',f'{out}/%(title)s.%(ext)s',url]
    subprocess.run(cmd, check=False)


def find_user():
    handle = ask('Enter a public username/handle (without @):').lstrip('@').strip()
    if not re.match(r'^[A-Za-z0-9._-]{2,50}$', handle): print(f'{R}Invalid handle.{X}'); return
    sites = {'GitHub':f'https://github.com/{handle}','YouTube':f'https://www.youtube.com/@{handle}','Instagram':f'https://www.instagram.com/{handle}/','X':f'https://x.com/{handle}','TikTok':f'https://www.tiktok.com/@{handle}'}
    print(f'{Y}This checks public profile links only; it does not search for phone numbers, email addresses, or private data.{X}')
    for name, url in sites.items():
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'255Tools/1.0'})
            with urllib.request.urlopen(req, timeout=8) as r: print(f'{G}[FOUND/OPEN] {name}: {url} ({r.status}){X}')
        except Exception: print(f'{Y}[not verified] {name}: {url}{X}')


def developer():
    print(f'{B}Developer: MrCodex1Tz{X}')
    print('Facebook name: MrCodex1Tz')
    print('255Tools is a project for learning Termux, safe networking, and APIs.')
    print(f'{Y}Do not use it for phishing, spam, fake engagement, doxxing, or privacy violations.{X}')


def main():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls'); print(G+BANNER+X)
        print(f'{B}255Tools — Educational Termux Toolkit{X}\n')
        print('1. Domain checker\n2. Temp mail (mail.tm demo)\n3. YouTube Growth Audit\n4. Download video (yt-dlp)\n5. Find public username\n6. Developer\n0. Exit')
        c=ask('Choose a feature:')
        if c=='1': domain_check()
        elif c=='2': temp_mail()
        elif c=='3': youtube_audit()
        elif c=='4': download_video()
        elif c=='5': find_user()
        elif c=='6': developer()
        elif c=='0': print('Goodbye.'); break
        else: print(f'{R}Invalid choice.{X}')
        input(f'\n{C}Press Enter to continue...{X}')

if __name__ == '__main__': main()
