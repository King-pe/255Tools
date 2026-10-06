#!/usr/bin/env python3
"""255Tools: safe, educational Termux utilities."""
from __future__ import annotations
import getpass, json, os, re, shutil, socket, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

G = '\033[92m'; B = '\033[94m'; C = '\033[96m'; Y = '\033[93m'; R = '\033[91m'; X = '\033[0m'
DEFAULT_VIDIQ_BACKEND = 'https://255tools-backed.vercel.app'
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
        else: print(f'{Y}RDAP returned HTTP {e.code}; try again later.{X}')
    except Exception as e: print(f'{Y}Could not verify live: {e}{X}')


MAIL_API = 'https://api.mail.tm'


def mail_request(path, method='GET', payload=None, token=None):
    headers = {'User-Agent': '255Tools/1.0', 'Accept': 'application/json'}
    if token: headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(payload).encode() if payload is not None else None
    if data: headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(f'{MAIL_API}{path}', data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode('utf-8', errors='replace')
        return json.loads(body) if body else {}


def mail_login():
    address = ask('Email address:')
    password = getpass.getpass('Password (hidden): ')
    result = mail_request('/token', method='POST', payload={'address': address, 'password': password})
    return result['token'], address


def temp_mail():
    print(f'{Y}Use only an inbox you created and control. Do not use it for spam, bypasses, or fake accounts.{X}')
    print('1) Create inbox  2) Login and view inbox  3) Send email')
    choice = ask('Choose:')
    try:
        if choice == '1':
            domains = mail_request('/domains')['hydra:member']
            domain = domains[0]['domain']; username = ask('New username:') or f'user{os.getpid()}'
            address = f'{username}@{domain}'; password = getpass.getpass('New password (hidden): ')
            created = mail_request('/accounts', method='POST', payload={'address': address, 'password': password})
            print(f"{G}Inbox created: {created.get('address', address)}{X}")
            print(f'{Y}Keep the address and password private. Use option 2 to read messages.{X}')
        elif choice == '2':
            token, address = mail_login()
            page = mail_request('/messages?limit=20', token=token)
            messages = page.get('hydra:member', [])
            print(f'{G}{len(messages)} message(s) for {address}:{X}')
            for message in messages:
                sender = message.get('from', {}).get('address', 'unknown sender')
                print(f"- {message.get('createdAt', '')} | {sender} | {message.get('subject', '(no subject)')} | id={message.get('id')}")
            message_id = ask('Enter message id to read, or press Enter to finish:')
            if message_id:
                detail = mail_request(f'/messages/{urllib.parse.quote(message_id)}', token=token)
                print(detail.get('text') or detail.get('intro') or '(empty message)')
        elif choice == '3':
            token, _ = mail_login()
            recipient = ask('Recipient email:'); subject = ask('Subject:'); text = ask('Message:')
            sent = mail_request('/messages', method='POST', token=token, payload={'to': [{'address': recipient}], 'subject': subject, 'text': text})
            print(f"{G}Email sent. Message id: {sent.get('id', 'accepted')}{X}")
        else:
            print('Invalid choice.')
    except Exception as error:
        print(f'{R}Mail.tm error: {error}{X}')


def dns_check():
    domain = ask('Enter domain (example.com):').lower().strip()
    domain = re.sub(r'^https?://', '', domain).split('/')[0].rstrip('.')
    if not re.match(r'^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$', domain):
        print(f'{R}Invalid domain.{X}'); return
    print(f'{C}DNS check for {domain}{X}')
    try:
        infos = socket.getaddrinfo(domain, 443, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in infos})
        print(f'{G}A/AAAA: connected — {", ".join(addresses)}{X}')
    except socket.gaierror:
        print(f'{R}A/AAAA: no address found{X}')
    if shutil.which('dig'):
        for record in ('NS', 'MX', 'TXT'):
            result = subprocess.run(['dig', '+short', record, domain], capture_output=True, text=True, timeout=10)
            values = result.stdout.strip()
            print(f'{G}{record}: {values or "not found"}{X}')
    else:
        print(f'{Y}NS/MX/TXT checks need dig. Install it with: pkg install dnsutils{X}')
    print(f'{B}DNS records show configuration only; they do not verify website ownership or SSL.{X}')


def ip_lookup(target=None):
    target = (ask('Enter IP address, or press Enter for your public IP:').strip() if target is None else target.strip())
    if target and not re.match(r'^[0-9a-fA-F:.]+$', target):
        print(f'{R}Invalid IP address format.{X}'); return
    endpoint = 'https://ipwho.is/' + urllib.parse.quote(target) if target else 'https://ipwho.is/'
    try:
        data, _ = get(endpoint, timeout=15)
        info = json.loads(data)
        if not info.get('success', False):
            print(f'{R}IP lookup failed: {info.get("message", "unknown error")}{X}'); return
        connection = info.get('connection') or {}
        timezone = info.get('timezone') or {}
        print(f'{G}IP location information:{X}')
        print(f'  IP: {info.get("ip", "unknown")}')
        print(f'  Country: {info.get("country", "unknown")} ({info.get("country_code", "")})')
        print(f'  Region: {info.get("region", "unknown")}')
        print(f'  City: {info.get("city", "unknown")}')
        print(f'  Latitude: {info.get("latitude", "unknown")}')
        print(f'  Longitude: {info.get("longitude", "unknown")}')
        print(f'  ISP: {connection.get("isp", "unknown")}')
        print(f'  Organization: {connection.get("org", "unknown")}')
        print(f'  ASN: {connection.get("asn", "unknown")}')
        print(f'  Timezone: {timezone.get("id", "unknown")}')
        print(f'{Y}Note: IP geolocation is approximate. It cannot reliably identify a person or exact street address.{X}')
    except Exception as error:
        print(f'{R}IP lookup error: {error}{X}')


def my_ip():
    print(f'{C}Looking up your public IP...{X}')
    ip_lookup('')


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
    sites = {'GitHub':f'https://github.com/{handle}','YouTube':f'https://www.youtube.com/@{handle}','Facebook':f'https://www.facebook.com/{handle}','Instagram':f'https://www.instagram.com/{handle}/','X':f'https://x.com/{handle}','TikTok':f'https://www.tiktok.com/@{handle}'}
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
        print('1. Domain checker\n2. Temp mail account\n3. Download video (yt-dlp)\n4. Social lookup (X/Twitter, Facebook, etc.)\n5. Domain DNS Check\n6. My IP\n7. IP Lookup\n8. Developer\n0. Exit')
        c=ask('Choose a feature:')
        if c=='1': domain_check()
        elif c=='2': temp_mail()
        elif c=='3': download_video()
        elif c=='4': find_user()
        elif c=='5': dns_check()
        elif c=='6': my_ip()
        elif c=='7': ip_lookup()
        elif c=='8': developer()
        elif c=='0': print('Goodbye.'); break
        else: print(f'{R}Invalid choice.{X}')
        input(f'\n{C}Press Enter to continue...{X}')

if __name__ == '__main__': main()
