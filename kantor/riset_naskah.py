"""Pekerja: Riset (cari topik), Penulis Naskah, Sutradara (pecah jadi adegan).
Memakai LLM gratis. Jika kunci berawalan 'gsk_' dipakai Groq, selain itu Gemini."""
import json
import os
import random
import re
import time

import requests

NICHE = os.getenv("NICHE", "fakta unik dan mengejutkan")

GROQ_URL = "https://api.groq.com/openai/v1"
GROQ_MODELS = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b",
               "openai/gpt-oss-20b", "llama-3.1-8b-instant"]
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.5-flash"]


def _json(teks):
    teks = re.sub(r"^```(?:json)?|```$", "", teks.strip(), flags=re.M).strip()
    try:
        return json.loads(teks)
    except ValueError:
        a, b = teks.find("{"), teks.rfind("}")
        return json.loads(teks[a:b + 1])


def _daftar_groq(key):
    """Daftar model Groq yang tersedia (cadangan jika nama model berubah)."""
    try:
        r = requests.get(GROQ_URL + "/models", timeout=30,
                         headers={"Authorization": f"Bearer {key}"})
        ids = [m["id"] for m in r.json().get("data", [])] if r.ok else []
    except Exception:
        return []
    buruk = ("whisper", "guard", "tts", "orpheus", "embed", "safeguard")
    ids = [i for i in ids if not any(b in i.lower() for b in buruk)]
    return sorted(ids, key=lambda i: not any(k in i for k in ("70b", "120b")))


def _openai(base, key, models, prompt):
    headers = {"Authorization": f"Bearer {key}"}
    galat = ""
    for model in models:
        for mode_json in (True, False):
            body = {"model": model, "temperature": 0.8,
                    "messages": [
                        {"role": "system",
                         "content": "Jawab HANYA dengan JSON valid, tanpa teks lain."},
                        {"role": "user", "content": prompt}]}
            if mode_json:
                body["response_format"] = {"type": "json_object"}
            for i in range(3):
                r = requests.post(base + "/chat/completions", headers=headers,
                                  json=body, timeout=90)
                if r.status_code != 429:
                    break
                time.sleep(15 * (i + 1))  # kena batas gratis, tunggu lalu coba lagi
            if r.ok:
                print("Model dipakai:", model, flush=True)
                return _json(r.json()["choices"][0]["message"]["content"])
            galat = f"{model} -> {r.status_code}: {r.text[:300]}"
            print("Gagal:", galat, flush=True)
            if r.status_code != 400:
                break  # 400 bisa berarti mode JSON tidak didukung: coba tanpa itu
        if r.status_code in (401, 403):
            break  # masalah kunci/izin, ganti model tidak membantu
    raise RuntimeError("LLM error. " + galat)


def _gemini(key, prompt):
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.9,
                                 "responseMimeType": "application/json"}}
    galat = ""
    for model in [m for m in [os.getenv("GEMINI_MODEL")] if m] + GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=90)
        if r.ok:
            bagian = r.json()["candidates"][0]["content"]["parts"]
            print("Model dipakai:", model, flush=True)
            return _json("".join(p.get("text", "") for p in bagian if not p.get("thought")))
        galat = f"{model} -> {r.status_code}: {r.text[:300]}"
        print("Gagal:", galat, flush=True)
        if r.status_code not in (404, 429):
            break
    raise RuntimeError("Gemini error. " + galat)


def gemini(prompt):  # nama dipertahankan supaya modul lain tidak perlu diubah
    key = (os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("Kunci API kosong. Cek nama secret di GitHub.")
    if key.startswith("gsk_"):
        awal = [m for m in [os.getenv("GROQ_MODEL")] if m] + GROQ_MODELS
        try:
            return _openai(GROQ_URL, key, awal, prompt)
        except RuntimeError as e:
            if "-> 404" not in str(e) and "-> 400" not in str(e):
                raise
            tambahan = [m for m in _daftar_groq(key) if m not in awal]
            return _openai(GROQ_URL, key, tambahan, prompt)
    return _gemini(key, prompt)


def cari_topik(riwayat):
    sudah = "; ".join(riwayat[-30:]) or "(belum ada)"
    hasil = gemini(
        f"Berikan 8 ide topik video YouTube Shorts berbahasa Indonesia "
        f"dengan niche: {NICHE}. Pilih topik yang faktanya mapan dan bisa "
        f"diverifikasi, bukan klaim kontroversial. Jangan ulangi topik ini: "
        f"{sudah}. Jawab JSON: {{\"topik\": [\"...\"]}}")
    return str(random.choice(hasil["topik"][:8]))


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
    for a in n["adegan"]:
        a.setdefault("visual", "nature landscape")
    n.setdefault("judul", topik[:70])
    n.setdefault("deskripsi", topik)
    n.setdefault("hashtag", ["#fakta", "#unik"])
    n["topik"] = topik
    return n
