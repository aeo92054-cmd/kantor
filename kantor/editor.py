"""Pekerja: Editor (rakit adegan + teks) dan Musik (campur soundtrack)."""
import random
import textwrap

from .util import FONT, run

MUSIK_EXT = {".mp3", ".m4a", ".wav", ".ogg"}


def _adegan(a, i, folder):
    if not FONT:
        raise RuntimeError("Font tidak ditemukan. Pasang fonts-dejavu-core "
                           "atau isi variabel FONT dengan path file .ttf")
    tf = folder / f"t{i}.txt"
    tf.write_text("\n".join(textwrap.wrap(a["narasi"], 24)), encoding="utf-8")
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920,fps=30,setsar=1,"
          f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=58:fontcolor=white:"
          "line_spacing=12:x=(w-text_w)/2:y=h*0.62:"
          "box=1:boxcolor=black@0.55:boxborderw=24")
    if a.get("klip"):
        masuk = ["-stream_loop", "-1", "-i", a["klip"]]
    else:  # tidak ada klip stok: latar warna polos
        masuk = ["-f", "lavfi", "-i", "color=c=0x1B2433:s=1080x1920:r=30"]
    out = folder / f"s{i}.mp4"
    run(["ffmpeg", "-y", *masuk, "-i", a["audio"], "-t", f"{a['dur'] + 0.35:.2f}",
         "-vf", vf, "-af", "apad", "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-ac", "2", out])
    return out


def rakit(adegan, folder, hasil):
    bagian = [_adegan(a, i, folder) for i, a in enumerate(adegan)]
    daftar = folder / "daftar.txt"
    daftar.write_text("".join(f"file '{p.resolve()}'\n" for p in bagian))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", daftar,
         "-c", "copy", hasil])
    return hasil


def tambah_musik(video, folder_musik, hasil):
    lagu = [p for p in folder_musik.glob("*") if p.suffix.lower() in MUSIK_EXT]
    if not lagu:
        video.replace(hasil)
        return None
    pilih = random.choice(lagu)
    run(["ffmpeg", "-y", "-i", video, "-stream_loop", "-1", "-i", pilih,
         "-filter_complex",
         "[1:a]volume=0.12[m];[0:a][m]amix=inputs=2:duration=first:"
         "dropout_transition=0[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
         "-shortest", hasil])
    return pilih.name
