from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import requests
import re
import time
from org.mozilla.javascript import Context  # pas disponible sur Render, on simule avec requests

app = FastAPI(title="Streamtape Extractor - Amagno Zone Grise 😈")

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

@app.get("/extract")
async def extract(url: str):
    if not "streamtape" in url:
        raise HTTPException(400, "Donne un lien Streamtape valide")

    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        html = r.text

        # Recherche du script JS obfuscé (comme dans CloudStream)
        script_match = re.search(r'<script[^>]*>(.*?get_player.*?</script>)', html, re.DOTALL)
        if not script_match:
            raise ValueError("Pas de script get_player trouvé")

        script = script_match.group(1)

        # Extrait l'argument get_player (simplifié, pas Rhino sur Render)
        arg_match = re.search(r"get_player`\('([^']+)'\)`", script)
        if arg_match:
            arg = arg_match.group(1)
            # Construit le lien (comme dans CloudStream)
            video_url = f"https://stape.fun/get_video?id={arg}&stream=1"

            # Bypass timer
            time.sleep(10)

            # Follow redirect
            r2 = requests.get(video_url, headers={"Referer": url}, allow_redirects=True, timeout=15)
            final_url = r2.url

            return {"status": "success", "direct_link": final_url}

        raise ValueError("Aucun argument get_player trouvé")

    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/")
async def root():
    return {"message": "Streamtape Extractor - utilise /extract?url=ton-lien"}
