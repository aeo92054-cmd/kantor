"""Pekerja: Riset (cari topik), Penulis Naskah, Sutradara (pecah jadi adegan).
Memakai Gemini API (tier gratis) lewat REST."""
import json
import os
import random
import time

import requests

# Urutan model yang dicoba. Bisa diganti lewat variabel GEMINI_MODEL.
MODELS = [m for m in [os.getenv("GEMINI_MODEL"), "gemini-3.8-flash",
                      "gemini-flash-latest", "gemini-3.5-flash"] if m]
NICHE = os.getenv("NICHE", "fakta unik dan mengejutkan")


def _panggil(model, body, headers):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    for i in range(3):
        r = requests.post(url, headers=headers, json=body, timeout=90)
        if r.status_code == 429:  # kena batas tier gratis, tunggu lalu coba lagi
            time.sleep(20 * (i + 1))
            continue
        return r
    return r


def gemini(prompt):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.9,
                                 "responseMimeType": "application/json"}}
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY kosong. Cek nama secret di GitHub.")
    headers = {"x-goog-api-key": key}
    galat = ""
    for model in MODELS:
        r = _panggil(model, body, headers)
        if r.ok:
            bagian = r.json()["candidates"][0]["content"]["parts"]
            teks = "".join(p.get("text", "") for p in bagian if not p.get("thought"))
            print("Model dipakai:", model, flush=True)
            return json.loads(teks)
        galat = f"{model} -> {r.status_code}: {r.text[:300]}"
        print("Gagal:", galat, flush=True)
        if r.status_code not in (404, 429):
            break  # error lain (mis. 403) tidak akan beres dengan ganti model
    raise RuntimeError("Gemini error. " + galat)


def cari_topik(riwayat):
    sudah = "; ".join(riwayat[-30:]) or "(belum ada)"
    hasil = gemini(
        f"Berikan 8 ide topik video YouTube Shorts berbahasa Indonesia "
        f"dengan niche: {NICHE}. Pilih topik yang faktanya mapan dan bisa "
        f"diverifikasi, bukan klaim kontroversial. Jangan ulangi topik ini: "
        f"{sudah}. Jawab JSON: {{\"topik\": [\"...\"]}}")
    return random.choice(hasil["topik"][:8])


def tulis_naskah(topik):
    n = gemini(f"""Kamu penulis naskah YouTube Shorts berbahasa Indonesia.
Topik: {topik}
Aturan:
- Total narasi 90-110 kata (sekitar 35-45 detik dibaca).
- 5 sampai 7 adegan. Adegan pertama adalah hook yang bikin penasaran.
- Adegan terakhir mengajak follow atau komen.
- Hanya fakta yang benar dan bisa diverifikasi. Jangan mengarang angka.
- Tiap adegan: narasi 1-2 kalimat pendek, dan "visual" berisi 2-4 kata
  kunci BAHASA INGGRIS untuk mencari video stok vertikal yang cocok.
Jawab JSON persis seperti ini:
{{"judul": "maks 70 karakter", "deskripsi": "1-2 kalimat",
 "hashtag": ["#fakta", "#unik"],
 "adegan": [{{"narasi": "...", "visual": "deep sea ocean"}}]}}""")
    assert n.get("adegan"), "Naskah kosong"
    n["topik"] = topik
    return n
