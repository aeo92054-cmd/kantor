"""Pekerja: Pengisi Suara. Memakai edge-tts (gratis, tidak resmi)."""
import asyncio
import os

import edge_tts

from .util import durasi

VOICE = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")  # atau id-ID-GadisNeural
RATE = os.getenv("TTS_RATE", "+8%")


async def _simpan(teks, path):
    await edge_tts.Communicate(teks, VOICE, rate=RATE).save(str(path))


def rekam(adegan, folder):
    for i, a in enumerate(adegan):
        p = folder / f"a{i}.mp3"
        asyncio.run(_simpan(a["narasi"], p))
        a["audio"] = p
        a["dur"] = durasi(p)
    return sum(a["dur"] for a in adegan)
