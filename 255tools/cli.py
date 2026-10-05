#!/usr/bin/env python3
"""255Tools: safe, educational Termux utilities."""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

G = '\033[92m'; B = '\033[94m'; C = '\033[96m'; Y = '\033[93m'; R = '\033[91m'; X = '\033[0m'
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
    domain = ask('Ingiza domain (mfano example.com):').lower().strip()
    domain = re.sub(r'^https?://', '', domain).split('/')[0]
    if not re.match(r'^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$', domain):
        print(f'{R}Domain si sahihi.{X}'); return
    try:
        data, _ = get(f'https://rdap.org/domain/{urllib.parse.quote(domain)}')
        obj = json.loads(data)
        status = ', '.join(obj.get('status', [])) or 'unknown'
        print(f'{G}Domain inaonekana imesajiliwa / taarifa ipo.{X}')
        print(f'  Domain: {domain}\n  Status: {status}')
    except urllib.error.HTTPError as e:
        if e.code == 404: print(f'{G}Inaonekana domain haijasajiliwa (available candidate).{X}')
        else: print(f'{Y}RDAP imerudisha HTTP {e.code}; jaribu tena baadaye.{X}')
    except Exception as e: print(f'{Y}Haikuweza kuthibitisha live: {e}{X}')


def temp_mail():
    print(f'{Y}Elimu tu: tumia inbox hii kwa majaribio halali, si spam, bypass au akaunti za udanganyifu.{X}')
    print('1) Tengeneza inbox ya muda  2) Angalia inbox  3) Tuma ujumbe')
    choice = ask('Chagua:')
    if choice == '1':
        try:
            domains = json.loads(get('https://api.mail.tm/domains')[0])['hydra:member']
            domain = domains[0]['domain']; username = ask('Username mpya:') or f'user{os.getpid()}'
            address = f'{username}@{domain}'; password = ask('Password (itaonekana wakati wa kuandika):')
            payload = json.dumps({'address': address, 'password': password}).encode()
            req = urllib.request.Request('https://api.mail.tm/accounts', data=payload, headers={'Content-Type':'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=15) as r:
                created = json.loads(r.read())
                print(f"{G}Inbox imeundwa: {created.get('address', address)}{X}")
            print(f'{Y}Hifadhi address na password kwa matumizi ya baadaye.{X}')
        except Exception as e: print(f'{R}Mail.tm error: {e}{X}')
    elif choice in ('2','3'):
        print(f'{Y}Kwa usalama, login/token management imeachwa wazi kwenye tutorial. Tumia mail.tm API docs na usitumie kwa spam.{X}')
    else: print('Chaguo si sahihi.')


def youtube_audit():
    url = ask('Bandika channel URL:')
    if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', url): print(f'{R}YouTube URL si sahihi.{X}'); return
    print(f'{G}Growth Audit ya kielimu:{X}')
    print('• Hakuna followers/subscribers bandia wanaoongezwa.')
    print('• Boresha title, thumbnail, retention, consistency na SEO.')
    print('• Kwa analytics za kina, fungua vidIQ au YouTube Studio ukiwa ume-login mwenyewe.')
    print(f'{B}URL yako: {url}{X}')


def download_video():
    url = ask('Bandika URL ya video:')
    if not url.startswith(('http://','https://')): print(f'{R}URL si sahihi.{X}'); return
    if not shutil.which('yt-dlp'):
        print(f'{Y}yt-dlp haipo. Sakinisha: pkg update && pkg install python ffmpeg && pip install -U yt-dlp{X}'); return
    print(f'{Y}Pakua tu video unazoruhusiwa kuhifadhi; heshimu copyright na Terms of Service.{X}')
    out = ask('Folder [downloads]:') or 'downloads'; Path(out).mkdir(exist_ok=True)
    cmd = ['yt-dlp','-f','bv*[height<=250]+ba/b[height<=250]/best','-o',f'{out}/%(title)s.%(ext)s',url]
    subprocess.run(cmd, check=False)


def find_user():
    handle = ask('Ingiza public username/handle (bila @):').lstrip('@').strip()
    if not re.match(r'^[A-Za-z0-9._-]{2,50}$', handle): print(f'{R}Handle si sahihi.{X}'); return
    sites = {'GitHub':f'https://github.com/{handle}','YouTube':f'https://www.youtube.com/@{handle}','Instagram':f'https://www.instagram.com/{handle}/','X':f'https://x.com/{handle}','TikTok':f'https://www.tiktok.com/@{handle}'}
    print(f'{Y}Hii inakagua public profile links tu; haitafuti namba, email au data binafsi.{X}')
    for name, url in sites.items():
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'255Tools/1.0'})
            with urllib.request.urlopen(req, timeout=8) as r: print(f'{G}[FOUND/OPEN] {name}: {url} ({r.status}){X}')
        except Exception: print(f'{Y}[haijathibitishwa] {name}: {url}{X}')


def developer():
    print(f'{B}Developer: MrCodex1Tz{X}')
    print('Facebook name: MrCodex1Tz')
    print('255Tools ni project ya kujifunza Termux, networking salama na APIs.')
    print(f'{Y}Usitumie kwa phishing, spam, fake engagement, doxxing au uvunjaji wa faragha.{X}')


def main():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls'); print(G+BANNER+X)
        print(f'{B}255Tools — Educational Termux Toolkit{X}\n')
        print('1. Domain checker\n2. Temp mail (mail.tm demo)\n3. YouTube Growth Audit\n4. Download video (yt-dlp)\n5. Find public username\n6. Developer\n0. Toka')
        c=ask('Chagua kipengele:')
        if c=='1': domain_check()
        elif c=='2': temp_mail()
        elif c=='3': youtube_audit()
        elif c=='4': download_video()
        elif c=='5': find_user()
        elif c=='6': developer()
        elif c=='0': print('Kwaheri.'); break
        else: print(f'{R}Chaguo si sahihi.{X}')
        input(f'\n{C}Bonyeza Enter kuendelea...{X}')

if __name__ == '__main__': main()
