#!/usr/bin/env python3
"""255Tools: safe, educational Termux utilities."""
from __future__ import annotations
import datetime, getpass, json, os, re, shutil, socket, ssl, subprocess, sys, urllib.parse, urllib.request
import time
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


def port_scanner():
    print(f'{Y}Scan only systems you own or have explicit permission to test.{X}')
    target = ask('Enter IP address or domain:').strip()
    if not re.match(r'^[A-Za-z0-9.:-]+$', target) or len(target) > 253:
        print(f'{R}Invalid target.{X}'); return
    raw_ports = ask('Ports [common, or e.g. 80,443,8000-8010]:').strip().lower()
    common = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 587, 993, 995, 3306, 3389, 5432, 8080]
    ports = set(common) if not raw_ports or raw_ports == 'common' else set()
    if raw_ports and raw_ports != 'common':
        try:
            for item in raw_ports.split(','):
                item = item.strip()
                if '-' in item:
                    start, end = (int(x) for x in item.split('-', 1))
                    if end < start or end - start > 1000: raise ValueError
                    ports.update(range(start, end + 1))
                else:
                    ports.add(int(item))
        except ValueError:
            print(f'{R}Invalid port list or range.{X}'); return
    ports = sorted(p for p in ports if 1 <= p <= 65535)
    if not ports or len(ports) > 100:
        print(f'{R}Choose between 1 and 100 valid ports.{X}'); return
    try:
        address = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)[0][4][0]
    except socket.gaierror:
        print(f'{R}Could not resolve target.{X}'); return
    print(f'{C}Scanning {target} ({address}) — {len(ports)} port(s){X}')
    open_ports = []
    for port in ports:
        is_ipv6 = ':' in address
        sock = socket.socket(socket.AF_INET6 if is_ipv6 else socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.7)
        try:
            endpoint = (address, port, 0, 0) if is_ipv6 else (address, port)
            if sock.connect_ex(endpoint) == 0:
                open_ports.append(port)
                print(f'{G}OPEN     {port}/tcp{X}')
        finally:
            sock.close()
    if not open_ports:
        print(f'{Y}No tested TCP ports reported open. Closed and filtered ports are not shown.{X}')
    else:
        print(f'{G}Open ports: {", ".join(map(str, open_ports))}{X}')


def wifi_scanner():
    print(f'{Y}Scan and connect only to Wi-Fi networks you own or are authorized to use.{X}')
    if not shutil.which('termux-wifi-scaninfo'):
        print(f'{R}Termux:API is not installed. Install the Termux:API app and run: pkg install termux-api{X}')
        return
    print('1. Scan nearby Wi-Fi networks\n2. Connect to an authorized network')
    choice = ask('Choose:')
    if choice == '1':
        try:
            result = subprocess.run(['termux-wifi-scaninfo'], capture_output=True, text=True, timeout=20)
            if result.returncode != 0: raise RuntimeError(result.stderr.strip() or 'scan failed')
            networks = json.loads(result.stdout or '[]')
            if not networks:
                print(f'{Y}No networks returned. Enable location permission and Wi-Fi scanning on Android.{X}')
                return
            print(f'{G}Nearby Wi-Fi networks:{X}')
            for item in networks:
                ssid = item.get('ssid') or '(hidden SSID)'
                security = item.get('capabilities') or item.get('security') or 'unknown security'
                strength = item.get('level', '?')
                print(f'  {ssid} | signal: {strength} dBm | {security}')
        except Exception as error:
            print(f'{R}Wi-Fi scan error: {error}{X}')
    elif choice == '2':
        if not shutil.which('termux-wifi-connect'):
            print(f'{R}Your installed Termux:API does not provide termux-wifi-connect.{X}')
            print(f'{Y}Use Android Wi-Fi settings to connect, then use option 1 to scan.{X}')
            return
        ssid = ask('Authorized Wi-Fi name (SSID):')
        password = getpass.getpass('Wi-Fi password (hidden): ')
        try:
            result = subprocess.run(['termux-wifi-connect', '-s', ssid, '-p', password], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f'{G}Connection request sent for {ssid}.{X}')
            else:
                print(f'{R}Wi-Fi connection failed: {result.stderr.strip() or "unknown error"}{X}')
        except Exception as error:
            print(f'{R}Wi-Fi connection error: {error}{X}')
    else:
        print('Invalid choice.')


def internet_speed():
    print(f'{Y}Speed test uses a limited public download sample; results are approximate.{X}')
    try:
        start = time.perf_counter()
        with urllib.request.urlopen('https://speed.cloudflare.com/__down?bytes=10000000', timeout=30) as response:
            total = 0
            while True:
                chunk = response.read(256 * 1024)
                if not chunk: break
                total += len(chunk)
        elapsed = max(time.perf_counter() - start, 0.001)
        mbps = (total * 8 / elapsed) / 1_000_000
        print(f'{G}Download: {mbps:.2f} Mbps ({total / 1_000_000:.1f} MB in {elapsed:.2f}s){X}')
        ping_start = time.perf_counter()
        get('https://speed.cloudflare.com/cdn-cgi/trace', timeout=10)
        latency = (time.perf_counter() - ping_start) * 1000
        print(f'{G}HTTP latency: {latency:.0f} ms{X}')
        print(f'{Y}Upload speed is not measured in this lightweight Termux test.{X}')
    except Exception as error:
        print(f'{R}Speed test error: {error}{X}')


def dns_links():
    providers = {
        '1': ('AdGuard DNS', '94.140.14.14 / 94.140.15.15', 'dns.adguard-dns.com', 'https://dns.adguard-dns.com/dns-query', 'Blocks many ads and trackers.'),
        '2': ('Cloudflare 1.1.1.1', '1.1.1.1 / 1.0.0.1', 'one.one.one.one', 'https://cloudflare-dns.com/dns-query', 'Fast resolver; does not block all ads by default.'),
        '3': ('Quad9', '9.9.9.9 / 149.112.112.112', 'dns.quad9.net', 'https://dns.quad9.net/dns-query', 'Blocks many malicious domains; not an ad blocker.'),
    }
    print('1. AdGuard DNS (ad/tracker blocking)\n2. Cloudflare (speed)\n3. Quad9 (malware blocking)')
    choice = ask('Choose DNS provider:')
    provider = providers.get(choice)
    if not provider:
        print('Invalid choice.'); return
    name, ips, private_dns, doh, purpose = provider
    print(f'{G}{name}{X} — {purpose}')
    print(f'IPv4: {ips}')
    print(f'Android Private DNS hostname: {private_dns}')
    print(f'DNS-over-HTTPS link: {doh}')
    print(f'{Y}Open Android Settings → Network & internet → Private DNS, then enter the hostname above.{X}')
    print(f'{Y}This prints a provider link; it does not create or host a private DNS server.{X}')


def headers_ssl_check():
    raw_url = ask('Enter URL or domain (example.com):').strip()
    url = raw_url if re.match(r'^https?://', raw_url, re.I) else f'https://{raw_url}'
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname
    if not hostname or not re.match(r'^[A-Za-z0-9.-]+$', hostname):
        print(f'{R}Invalid URL or hostname.{X}'); return
    print(f'{C}HTTP headers for {url}{X}')
    try:
        request = urllib.request.Request(url, method='HEAD', headers={'User-Agent': '255Tools/1.0'})
        try:
            response = urllib.request.urlopen(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        print(f'{G}HTTP status: {response.status}{X}')
        sensitive = {'set-cookie', 'cookie', 'authorization', 'proxy-authorization'}
        for key, value in response.headers.items():
            shown = '[redacted]' if key.lower() in sensitive else value
            print(f'  {key}: {shown}')
        response.close()
    except Exception as error:
        print(f'{Y}HTTP header check failed: {error}{X}')
    print(f'{C}SSL certificate for {hostname}{X}')
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=15) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=hostname) as tls_socket:
                certificate = tls_socket.getpeercert()
                expires_raw = certificate.get('notAfter')
                expires = datetime.datetime.fromtimestamp(ssl.cert_time_to_seconds(expires_raw), datetime.timezone.utc) if expires_raw else None
                now = datetime.datetime.now(datetime.timezone.utc)
                print(f'{G}Certificate valid: yes{X}')
                print(f'  TLS version: {tls_socket.version()}')
                print(f'  Subject: {certificate.get("subject", "unknown")}')
                print(f'  Issuer: {certificate.get("issuer", "unknown")}')
                print(f'  Expires: {expires.isoformat() if expires else "unknown"}')
                if expires: print(f'  Days remaining: {(expires - now).days}')
    except ssl.SSLCertVerificationError as error:
        print(f'{R}Certificate valid: no — verification failed: {error}{X}')
    except Exception as error:
        print(f'{Y}SSL check failed: {error}{X}')


def phone_lookup():
    raw = ask('Enter phone number with country code (example +255712345678):').strip()
    compact = re.sub(r'[\s().-]', '', raw)
    if not re.match(r'^\+[1-9]\d{7,14}$', compact):
        print(f'{R}Use international E.164 format, for example +255712345678.{X}'); return
    country_codes = {
        '+1': 'US/Canada and NANP regions', '+20': 'Egypt', '+27': 'South Africa', '+30': 'Greece',
        '+33': 'France', '+34': 'Spain', '+39': 'Italy', '+44': 'United Kingdom', '+49': 'Germany',
        '+52': 'Mexico', '+55': 'Brazil', '+61': 'Australia', '+81': 'Japan', '+82': 'South Korea',
        '+86': 'China', '+91': 'India', '+212': 'Morocco', '+234': 'Nigeria', '+254': 'Kenya',
        '+255': 'Tanzania', '+256': 'Uganda', '+260': 'Zambia', '+263': 'Zimbabwe', '+267': 'Botswana',
        '+971': 'United Arab Emirates', '+972': 'Israel', '+974': 'Qatar', '+966': 'Saudi Arabia',
    }
    matched = next((code for code in sorted(country_codes, key=len, reverse=True) if compact.startswith(code)), None)
    print(f'{G}Phone number metadata:{X}')
    print(f'  Normalized: {compact}')
    print(f'  Country code: {matched or "unknown"}')
    print(f'  Country/region: {country_codes.get(matched, "unknown") if matched else "unknown"}')
    print(f'  Possible international format: yes')
    print(f'{Y}Privacy note: this tool does not identify the owner, reveal an address, track live location, or search private social accounts.{X}')


def tz_network_check():
    raw = ask('Enter Tanzania number (+255..., 255..., or 07...):').strip()
    compact = re.sub(r'[\s().-]', '', raw)
    if compact.startswith('+255'):
        local = '0' + compact[4:]
    elif compact.startswith('255'):
        local = '0' + compact[3:]
    elif compact.startswith('0'):
        local = compact
    else:
        print(f'{R}Use a Tanzania number beginning with +255, 255, or 0.{X}'); return
    if not re.match(r'^0[67]\d{8}$', local):
        print(f'{R}Invalid Tanzania mobile number format.{X}'); return
    prefix = local[:3]
    networks = {
        '061': 'Halotel', '062': 'Halotel',
        '065': 'Tigo / Yas', '067': 'Tigo / Yas', '071': 'Tigo / Yas',
        '068': 'Airtel', '069': 'Airtel', '078': 'Airtel',
        '074': 'Vodacom', '075': 'Vodacom', '076': 'Vodacom',
        '073': 'TTCL',
    }
    print(f'{G}Tanzania number information:{X}')
    print(f'  E.164 format: +255{local[1:]}')
    print(f'  Prefix: {prefix}')
    print(f'  Likely network allocation: {networks.get(prefix, "Unknown or unlisted allocation")}')
    print(f'{Y}Important: mobile number portability means the prefix may not show the current network.{X}')
    print(f'{Y}Subscriber registration (NIDA/name/ID/address) is private and is not available through this tool.{X}')


def email_breach_lookup():
    email = ask('Enter your email address:').strip()
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$', email):
        print(f'{R}Invalid email address.{X}'); return
    print(f'{Y}This sends the email to Have I Been Pwned only after you request the check. Never enter an email you do not control.{X}')
    api_key = getpass.getpass('HIBP API key (hidden): ').strip()
    if not api_key:
        print(f'{R}A Have I Been Pwned API key is required for breach lookup.{X}'); return
    encoded = urllib.parse.quote(email, safe='')
    headers = {'hibp-api-key': api_key, 'user-agent': '255Tools/1.0 defensive email safety check'}
    try:
        data, _ = get(f'https://haveibeenpwned.com/api/v3/breachedaccount/{encoded}?truncateResponse=false', headers=headers, timeout=20)
        breaches = json.loads(data)
        if not breaches:
            print(f'{G}No breaches were returned for this email.{X}')
            return
        print(f'{R}This email appeared in {len(breaches)} reported breach(es):{X}')
        for breach in breaches:
            classes = ', '.join(breach.get('DataClasses', []))
            print(f"- {breach.get('Name', 'unknown')} | date: {breach.get('BreachDate', 'unknown')} | exposed categories: {classes}")
        print(f'{Y}Change reused passwords and enable MFA. This tool never displays passwords or recovery secrets.{X}')
    except urllib.error.HTTPError as error:
        if error.code == 404:
            print(f'{G}No breaches were returned for this email.{X}')
        elif error.code == 401:
            print(f'{R}HIBP API key was rejected.{X}')
        elif error.code == 429:
            print(f'{Y}HIBP rate limit reached; try again later.{X}')
        else:
            print(f'{R}HIBP returned HTTP {error.code}.{X}')
    except Exception as error:
        print(f'{R}Email breach lookup error: {error}{X}')


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
        print('1. Domain checker\n2. Temp mail account\n3. Download video (yt-dlp)\n4. Social lookup (X/Twitter, Facebook, etc.)\n5. Domain DNS Check\n6. My IP\n7. IP Lookup\n8. Port Scanner\n9. Wi-Fi Scanner\n10. Internet Speed\n11. DNS Server Links\n12. HTTP Headers & SSL Check\n13. Phone Number Safety Check\n14. Tanzania Network Check\n15. Email Breach Safety Check\n16. Developer\n0. Exit')
        c=ask('Choose a feature:')
        if c=='1': domain_check()
        elif c=='2': temp_mail()
        elif c=='3': download_video()
        elif c=='4': find_user()
        elif c=='5': dns_check()
        elif c=='6': my_ip()
        elif c=='7': ip_lookup()
        elif c=='8': port_scanner()
        elif c=='9': wifi_scanner()
        elif c=='10': internet_speed()
        elif c=='11': dns_links()
        elif c=='12': headers_ssl_check()
        elif c=='13': phone_lookup()
        elif c=='14': tz_network_check()
        elif c=='15': email_breach_lookup()
        elif c=='16': developer()
        elif c=='0': print('Goodbye.'); break
        else: print(f'{R}Invalid choice.{X}')
        input(f'\n{C}Press Enter to continue...{X}')

if __name__ == '__main__': main()
