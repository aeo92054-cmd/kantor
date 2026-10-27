"""Fungsi bersama: log antar pekerja, menjalankan ffmpeg, mengukur durasi."""
import datetime
import json
import os
import pathlib
import subprocess

OUT = pathlib.Path("output")
EVENTS = []

_FONTS = [
    os.getenv("FONT", ""),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]
FONT = next((f for f in _FONTS if f and os.path.exists(f)), None)


def log(dari, ke, pesan):
    """Catat 'percakapan' antar pekerja. Disimpan ke output/log.json
    supaya nanti bisa diputar ulang oleh website kantor."""
    e = {"waktu": datetime.datetime.now().strftime("%H:%M:%S"),
         "dari": dari, "ke": ke, "pesan": pesan}
    EVENTS.append(e)
    print(f"[{e['waktu']}] {dari} -> {ke}: {pesan}", flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "log.json").write_text(
        json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding="utf-8")


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("Perintah gagal: " + " ".join(map(str, cmd))
                           + "\n" + r.stderr[-1500:])
    return r.stdout


def durasi(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", path])
    return float(out.strip())
