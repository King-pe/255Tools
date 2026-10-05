# 255Tools

**255Tools** ni toolkit ya Termux yenye muonekano wa kijani/bluu, iliyotengenezwa kwa ajili ya kujifunza Python, APIs, networking salama na matumizi halali ya command line.

## Vipengele

1. **Domain checker** — hutumia RDAP kuonyesha kama domain ina taarifa ya usajili.
2. **Temp mail demo** — huunganisha na mail.tm kwa majaribio halali ya inbox; usitumie kwa spam, bypass au akaunti bandia.
3. **YouTube Growth Audit** — mapendekezo ya ukuaji wa channel; haiongezi subscribers/followers bandia. Tumia YouTube Studio/vidIQ kwa analytics ukiwa ume-login mwenyewe.
4. **Video downloader** — wrapper wa `yt-dlp`, kwa video unazoruhusiwa kuhifadhi tu. Inalenga ubora wa karibu 250p inapopatikana.
5. **Public username finder** — hukagua links za public profiles pekee; haitafuti simu, email, location au taarifa binafsi.
6. **Developer** — taarifa za MrCodex1Tz.

> **MVP note:** Temp mail kwa sasa ina demo ya kuunda inbox kupitia mail.tm; login, kusoma inbox na kutuma ujumbe vitahitaji kuongezwa kwa session/token handling katika toleo linalofuata. Growth feature ni audit ya ukuaji tu—hakuna subscribers bandia.

## Usakinishaji Termux

```bash
pkg update -y
pkg install -y git
 git clone https://github.com/King-pe/255Tools.git
cd 255Tools
bash install.sh
255tools
```

## Kanuni ya matumizi

Hii ni project ya elimu. Usitumie kwa phishing, spam, fake engagement, doxxing, account takeover, kupita OTP/verification, au kuvunja Terms of Service. Code imeandikwa kwa uwazi na kwa mtindo unaosomeka kirahisi.
