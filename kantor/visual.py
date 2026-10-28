"""Pekerja: Pencari Visual. Mencari video stok gratis.
Urutan: Pexels (jika ada PEXELS_API_KEY), lalu Pixabay (jika ada PIXABAY_API_KEY)."""
import os
import random

import requests


def _unduh(url, path):
    r = requests.get(url, timeout=120)
    if not r.ok:
        return False
    path.write_bytes(r.content)
    return True


def _pexels(kata, folder, i, dipakai):
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return None
    r = requests.get("https://api.pexels.com/videos/search",
                     headers={"Authorization": key},
                     params={"query": kata, "orientation": "portrait",
                             "size": "medium", "per_page": 10}, timeout=30)
    if not r.ok:
        return None
    vids = [v for v in r.json().get("videos", []) if ("pe", v["id"]) not in dipakai]
    random.shuffle(vids)
    for v in vids:
        files = [f for f in v["video_files"]
                 if f.get("file_type") == "video/mp4" and f.get("width")
                 and f["width"] <= 1080 and f["height"] >= f["width"]]
        if not files:
            continue
        f = max(files, key=lambda x: x["width"])
        path = folder / f"k{i}.mp4"
        if _unduh(f["link"], path):
            dipakai.add(("pe", v["id"]))
            return path
    return None


def _pixabay(kata, folder, i, dipakai):
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return None
    r = requests.get("https://pixabay.com/api/videos/",
                     params={"key": key, "q": kata, "per_page": 20,
                             "safesearch": "true"}, timeout=30)
    if not r.ok:
        return None
    hits = [h for h in r.json().get("hits", []) if ("px", h["id"]) not in dipakai]
    random.shuffle(hits)
    for h in hits:
        v = h.get("videos", {})
        pilih = next((v[k] for k in ("large", "medium", "small")
                      if v.get(k, {}).get("url")), None)
        if not pilih:
            continue
        path = folder / f"k{i}.mp4"
        if _unduh(pilih["url"], path):
            dipakai.add(("px", h["id"]))
            return path
    return None


def cari_klip(kata, folder, i, dipakai):
    # Pixabay tidak punya filter vertikal; klip mendatar dipotong tengah oleh Editor.
    for q in (kata, kata.split()[0]):
        hasil = _pexels(q, folder, i, dipakai) or _pixabay(q, folder, i, dipakai)
        if hasil:
            return hasil
    return None
