"""Pekerja: QC. Memeriksa video sebelum boleh diunggah."""
import json

from .util import durasi, run


def periksa(path):
    masalah = []
    d = durasi(path)
    if not 15 <= d <= 58:
        masalah.append(f"Durasi {d:.1f} detik, harus 15-58 detik")
    info = json.loads(run(["ffprobe", "-v", "error", "-show_streams",
                           "-of", "json", path]))
    v = [s for s in info["streams"] if s["codec_type"] == "video"]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if not v or (v[0]["width"], v[0]["height"]) != (1080, 1920):
        masalah.append("Ukuran video bukan 1080x1920")
    if not a:
        masalah.append("Video tidak punya suara")
    return d, masalah
