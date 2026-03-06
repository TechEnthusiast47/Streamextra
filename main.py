from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import requests
import re
import time

app = FastAPI(title="Streamtape Extractor - Amagno Zone Grise 😈")

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

@app.get("/extract")
async def extract(url: str):
    if not url.startswith("https://streamtape"):
        raise HTTPException(status_code=400, detail="Donne-moi un vrai lien Streamtape stp")

    try:
        # Fetch la page avec UA mobile
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        html = r.text

        # Regex 2026 - on cherche les patterns classiques
        patterns = [
            r"get_player\('([^']+)'\)",
            r'file:\s*"([^"]+)"',
            r'src="([^"]+\.(mp4|m3u8))"',
            r"id=\"videolink\" href=\"([^\"]+)\""
        ]

        match = None
        for pat in patterns:
            m = re.search(pat, html)
            if m:
                match = m.group(1)
                break

        if not match:
            raise ValueError("Aucun lien vidéo trouvé - Streamtape a changé son HTML 😤")

        # Bypass timer (attente réelle)
        time.sleep(9)

        # Follow redirect
        r2 = requests.get(match, headers={"Referer": url}, allow_redirects=True, timeout=15)
        final_url = r2.url

        if ".mp4" not in final_url and ".m3u8" not in final_url:
            raise ValueError("Lien final pas un média valide")

        # On renvoie le lien direct (ou redirect direct si tu préfères)
        return {"status": "success", "direct_link": final_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Streamtape Extractor by Amagno - utilise /extract?url=ton-lien-streamtape"}
