"""Kantor Shorts: satu kali jalan = satu video YouTube Shorts.
Alur: Riset -> Penulis -> Sutradara -> Suara -> Visual -> Editor -> Musik -> QC -> Uploader
Hasil tiap video juga dicatat di docs/data/videos.json untuk website kantor."""
import datetime
import json
import os
import pathlib
import shutil
import sys

from kantor import editor, qc, riset_naskah, suara, visual
from kantor.util import EVENTS, OUT, log

RIWAYAT = pathlib.Path("history.json")
MUSIK = pathlib.Path("music")
SITUS = pathlib.Path("docs/data/videos.json")


def buat_video(riwayat):
    kerja = OUT / "kerja"
    shutil.rmtree(kerja, ignore_errors=True)
    kerja.mkdir(parents=True)

    topik = riset_naskah.cari_topik(riwayat)
    log("Si Pemburu Tren", "Penulis Naskah", f"Topik hari ini: “{topik}”. Tolong tulis naskahnya.")

    naskah = riset_naskah.tulis_naskah(topik)
    adegan = naskah["adegan"]
    kata = sum(len(a["narasi"].split()) for a in adegan)
    log("Penulis Naskah", "Sutradara", f"Naskah “{naskah['judul']}” selesai, {kata} kata.")
    log("Sutradara", "Pengisi Suara", f"{len(adegan)} adegan siap. Tolong rekam suaranya.")

    total = suara.rekam(adegan, kerja)
    log("Pengisi Suara", "Pencari Visual", f"Suara selesai, total {total:.0f} detik.")

    dipakai, ketemu = set(), 0
    for i, a in enumerate(adegan):
        a["klip"] = visual.cari_klip(a["visual"], kerja, i, dipakai)
        ketemu += bool(a["klip"])
    log("Pencari Visual", "Editor", f"{ketemu} dari {len(adegan)} klip ditemukan"
        + ("" if ketemu else " (pakai latar polos, isi PIXABAY_API_KEY atau PEXELS_API_KEY untuk klip stok)") + ".")

    mentah = editor.rakit(adegan, kerja, kerja / "mentah.mp4")
    log("Editor", "Musik", "Video dirakit dengan subtitle format 9:16. Tolong pasang soundtrack.")

    final = OUT / "final.mp4"
    lagu = editor.tambah_musik(mentah, MUSIK, final)
    log("Musik", "QC", f"Soundtrack: {lagu}." if lagu else "Folder music/ kosong, video tanpa musik latar.")

    d, masalah = qc.periksa(final)
    if masalah:
        raise RuntimeError("QC gagal: " + "; ".join(masalah))
    log("QC", "Uploader", f"Lolos QC ({d:.0f} detik, 1080x1920).")
    naskah["durasi"] = d
    (OUT / "meta.json").write_text(json.dumps(
        {k: naskah[k] for k in ("judul", "deskripsi", "hashtag", "topik")},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return final, naskah


def simpan_situs(naskah, status, youtube_id=None):
    """Tambahkan video ini ke data yang dibaca website kantor."""
    data = {"total": 0, "videos": []}
    if SITUS.exists():
        data = json.loads(SITUS.read_text(encoding="utf-8"))
    data["total"] += 1
    data["videos"].append({
        "id": f"VID-{data['total']}",
        "tanggal": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "judul": naskah["judul"], "topik": naskah["topik"],
        "hashtag": naskah["hashtag"], "durasi": round(naskah.get("durasi", 0)),
        "status": status, "youtube": youtube_id, "peristiwa": list(EVENTS)})
    data["videos"] = data["videos"][-20:]
    SITUS.parent.mkdir(parents=True, exist_ok=True)
    SITUS.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    riwayat = json.loads(RIWAYAT.read_text()) if RIWAYAT.exists() else []
    for percobaan in (1, 2):
        try:
            final, naskah = buat_video(riwayat)
            break
        except RuntimeError as e:
            log("Sistem", "Semua pekerja", f"Percobaan {percobaan} gagal: {str(e)[:200]}")
            if percobaan == 2:
                sys.exit(1)

    status, yt = "siap", None
    if os.getenv("UPLOAD") == "1":
        from kantor import uploader
        yt = uploader.unggah(final, naskah)
        status = "diunggah"
        log("Uploader", "Channel", f"Terunggah ({os.getenv('YT_PRIVACY', 'private')}): https://youtu.be/{yt}")
    else:
        log("Uploader", "Channel", "Upload dimatikan. Video siap di output/final.mp4.")

    simpan_situs(naskah, status, yt)
    riwayat.append(naskah["topik"])
    RIWAYAT.write_text(json.dumps(riwayat[-200:], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
