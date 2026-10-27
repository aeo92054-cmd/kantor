"""Kantor Shorts: satu kali jalan = satu video.
Alur: Riset -> Penulis -> Sutradara -> Suara -> Visual -> Editor -> Musik -> QC -> Uploader"""
import json
import os
import pathlib
import shutil
import sys

from kantor import editor, qc, riset_naskah, suara, visual
from kantor.util import OUT, log

RIWAYAT = pathlib.Path("history.json")
MUSIK = pathlib.Path("music")


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
        + ("" if ketemu else " (pakai latar polos, isi PEXELS_API_KEY untuk klip stok)") + ".")

    mentah = editor.rakit(adegan, kerja, kerja / "mentah.mp4")
    log("Editor", "Musik", "Video dirakit dengan subtitle format 9:16. Tolong pasang soundtrack.")

    final = OUT / "final.mp4"
    lagu = editor.tambah_musik(mentah, MUSIK, final)
    log("Musik", "QC", f"Soundtrack: {lagu}." if lagu else "Folder music/ kosong, video tanpa musik latar.")

    d, masalah = qc.periksa(final)
    if masalah:
        raise RuntimeError("QC gagal: " + "; ".join(masalah))
    log("QC", "Uploader", f"Lolos QC ({d:.0f} detik, 1080x1920).")
    (OUT / "meta.json").write_text(json.dumps(
        {k: naskah[k] for k in ("judul", "deskripsi", "hashtag", "topik")},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return final, naskah


def main():
    riwayat = json.loads(RIWAYAT.read_text()) if RIWAYAT.exists() else []
    for percobaan in (1, 2):
        try:
            final, naskah = buat_video(riwayat)
            break
        except RuntimeError as e:
            log("Sistem", "Semua pekerja", f"Percobaan {percobaan} gagal: {e}")
            if percobaan == 2:
                sys.exit(1)

    if os.getenv("UPLOAD") == "1":
        from kantor import uploader
        vid = uploader.unggah(final, naskah)
        log("Uploader", "Channel", f"Terunggah ({os.getenv('YT_PRIVACY', 'private')}): https://youtu.be/{vid}")
    else:
        log("Uploader", "Channel", "Upload dimatikan (UPLOAD!=1). Video disimpan di output/final.mp4.")

    riwayat.append(naskah["topik"])
    RIWAYAT.write_text(json.dumps(riwayat[-200:], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
