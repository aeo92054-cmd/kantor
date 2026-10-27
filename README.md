# Kantor Shorts

Satu kali jalan = satu video YouTube Shorts, dibuat oleh "pekerja" berurutan:

Riset -> Penulis Naskah -> Sutradara -> Pengisi Suara -> Pencari Visual -> Editor -> Musik -> QC -> Uploader

| Pekerja | File | Teknologi gratis |
|---|---|---|
| Riset, Penulis, Sutradara | `kantor/riset_naskah.py` | Gemini API (tier gratis) |
| Pengisi Suara | `kantor/suara.py` | edge-tts (suara bahasa Indonesia) |
| Pencari Visual | `kantor/visual.py` | Pexels API (video stok) |
| Editor, Musik | `kantor/editor.py` | FFmpeg |
| QC | `kantor/qc.py` | ffprobe |
| Uploader | `kantor/uploader.py` | YouTube Data API (opsional) |

Setiap serah-terima antar pekerja dicatat di `output/log.json`. Nanti file ini bisa dibaca website kantor supaya percakapannya asli, bukan simulasi.

## 1. Coba di komputer dulu (Linux / Mac / WSL)

1. Pasang Python 3.10+ dan FFmpeg (`sudo apt install ffmpeg fonts-dejavu-core`).
2. `pip install -r requirements.txt`
3. Ambil API key gratis:
   - Gemini: https://aistudio.google.com (menu API key)
   - Pexels: https://www.pexels.com/api/ (opsional, tanpa ini video memakai latar polos)
4. Jalankan:
   ```
   export GEMINI_API_KEY="isi_key"
   export PEXELS_API_KEY="isi_key"
   python main.py
   ```
5. Hasil ada di `output/final.mp4`. Tonton dulu sebelum lanjut ke otomatis.
6. Taruh beberapa lagu bebas hak cipta di folder `music/` (opsional). Cek lisensinya.

Variabel yang bisa diubah: `NICHE` (niche konten), `GEMINI_MODEL` (jika nama model berubah, cek di AI Studio), `TTS_VOICE` (`id-ID-ArdiNeural` atau `id-ID-GadisNeural`), `TTS_RATE`.

## 2. Jalan otomatis di GitHub Actions (gratis)

1. Buat repositori di GitHub dan unggah folder ini. Repositori publik = menit Actions gratis tanpa batas. Karena publik, JANGAN taruh key di kode.
2. Settings > Secrets and variables > Actions > Secrets: tambah `GEMINI_API_KEY` dan `PEXELS_API_KEY`.
3. Tab Actions > Kantor Shorts > Run workflow untuk mencoba. Hasil video ada di bagian Artifacts.
4. Setelah cocok, jadwal otomatis sudah aktif (default sekali sehari, ubah di `cron` pada `.github/workflows/shorts.yml`).

## 3. Upload otomatis ke YouTube (jalankan terakhir)

1. Google Cloud Console: buat proyek, aktifkan YouTube Data API v3, buat OAuth client tipe Desktop, unduh sebagai `client_secret.json`.
2. Di OAuth consent screen, setahu saya status "Testing" membuat refresh token kedaluwarsa dalam 7 hari. Jika ingin awet, ubah ke "In production" untuk pemakaian pribadi.
3. Jalankan `python get_youtube_token.py` sekali di komputer, login dengan akun channel, lalu simpan tiga nilainya sebagai Secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
4. Settings > Variables > Actions: buat `UPLOAD` = `1`. Secara default video diunggah sebagai privat (`YT_PRIVACY` = `private`).
5. Video dari proyek API yang belum diaudit YouTube akan terkunci privat. Ajukan audit kepatuhan YouTube API. Cek kuota di Cloud Console.
6. Beri tanda konten AI di YouTube Studio jika diwajibkan (cek pengaturan "altered content" di Studio). Deskripsi sudah memuat keterangan dibuat dengan bantuan AI.

## Catatan penting

- Periksa syarat penggunaan tier gratis Gemini untuk keperluan komersial, dan lisensi Pexels serta musik yang kamu pakai.
- edge-tts bukan layanan resmi dan bisa berhenti bekerja sewaktu-waktu. Siapkan alternatif (mis. Piper) jika perlu.
- Tonton tiap video sebelum dipublikasikan, terutama di awal. Fakta dari AI bisa salah. YouTube dapat menolak monetisasi konten massal tanpa nilai orisinal.
