"""Pekerja: Pencari Visual. Mengambil video stok vertikal dari Pexels (gratis)."""
import os
import random

import requests


def cari_klip(kata, folder, i, dipakai):
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return None
    r = requests.get("https://api.pexels.com/videos/search",
                     headers={"Authorization": key},
                     params={"query": kata, "orientation": "portrait",
                             "size": "medium", "per_page": 10}, timeout=30)
    if not r.ok:
        return None
    vids = [v for v in r.json().get("videos", []) if v["id"] not in dipakai]
    random.shuffle(vids)
    for v in vids:
        files = [f for f in v["video_files"]
                 if f.get("file_type") == "video/mp4" and f.get("width")
                 and f["width"] <= 1080 and f["height"] >= f["width"]]
        if not files:
            continue
        f = max(files, key=lambda x: x["width"])
        path = folder / f"k{i}.mp4"
        data = requests.get(f["link"], timeout=120)
        if not data.ok:
            continue
        path.write_bytes(data.content)
        dipakai.add(v["id"])
        return path
    return None
