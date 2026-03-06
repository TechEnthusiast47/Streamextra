from fastapi import FastAPI, HTTPException
import requests
import re
import time
from urllib.parse import urlparse

app = FastAPI(title="Streamtape Extractor - Amagno Zone Grise 😈")

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

@app.get("/extract")
async def extract(url: str):
    if not url.startswith("https://streamtape"):
        raise HTTPException(400, "Balance un vrai lien Streamtape, pas de blague")

    print(f"Extraction pour : {url}")

    try:
        # Fetch la page avec UA mobile + Referer
        headers = {
            "User-Agent": UA,
            "Referer": "https://streamtape.com/"
        }
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        html = r.text

        print(f"Page fetchée (status {r.status_code}), taille HTML: {len(html)} octets")

        # Regex 2026 plus large (inspiré CloudStream + tests récents)
        patterns = [
            r"get_player\('([^']+)'\)",               # pattern classique
            r"file:\s*[\"']([^\"']+)\"",              # file: "url"
            r"src=[\"']([^\"']+\.(mp4|m3u8))[\"']",   # src="...mp4"
            r"'([^']*?get_video[^']*?)'",             # get_video dans JS
            r"var\s+url\s*=\s*[\"']([^\"']+)\"",      # var url = "..."
            r"id=\"videolink\"[^>]*href=[\"']([^\"']+)",  # videolink href
        ]

        match = None
        for pattern in patterns:
            m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if m:
                match = m.group(1)
                print(f"Match trouvé avec pattern : {pattern}")
                break

        if not match:
            # Dump un bout du HTML pour debug
            debug_html = html[:1000] + "..." + html[-1000:]
            print(f"Aucun match - HTML snippet : {debug_html}")
            raise ValueError("Aucun lien vidéo détecté - Streamtape a changé son code (regarde les logs Render)")

        # Nettoyage du lien (parfois relatif)
        if match.startswith("/"):
            parsed = urlparse(url)
            match = f"{parsed.scheme}://{parsed.netloc}{match}"

        print(f"Lien extrait : {match}")

        # Bypass timer pub (obligatoire)
        print("Attente 10s pour bypass timer...")
        time.sleep(10)

        # Follow redirect avec Referer
        r2 = requests.get(match, headers={"Referer": url}, allow_redirects=True, timeout=15)
        final_url = r2.url

        print(f"Redirect final : {final_url}")

        if ".mp4" not in final_url and ".m3u8" not in final_url:
            raise ValueError(f"Lien final pas valide : {final_url}")

        return {
            "status": "success",
            "original_url": url,
            "direct_link": final_url
        }

    except Exception as e:
        print(f"Erreur extraction : {str(e)}")
        raise HTTPException(500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Streamtape Extractor by Amagno – utilise /extract?url=ton-lien-streamtape"}
