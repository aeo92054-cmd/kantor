"""Pekerja: Riset (cari topik), Penulis Naskah, Sutradara (pecah jadi adegan).
Memakai Gemini API (tier gratis) lewat REST."""
import json
import os
import random
import time

import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
NICHE = os.getenv("NICHE", "fakta unik dan mengejutkan")


def gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.9,
                                 "responseMimeType": "application/json"}}
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    print("Panjang key:", len(key), flush=True)
    if not key:
        raise RuntimeError("GEMINI_API_KEY kosong. Cek nama secret di GitHub.")
    headers = {"x-goog-api-key": key}
    for i in range(3):
        r = requests.post(url, headers=headers, json=body, timeout=90)
        if r.status_code == 429:  # kena batas tier gratis, tunggu lalu coba lagi
            time.sleep(20 * (i + 1))
            continue
        if not r.ok:
            raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:400]}")
        teks = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(teks)
    raise RuntimeError("Gemini kena batas pemakaian (429). Coba lagi nanti.")


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
