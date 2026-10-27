"""Pekerja: Uploader. Unggah ke YouTube lewat Data API (opsional)."""
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def unggah(path, meta):
    cred = Credentials(
        None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = build("youtube", "v3", credentials=cred)
    tag = [h.lstrip("#") for h in meta["hashtag"]]
    desk = (meta["deskripsi"] + "\n\n" + " ".join(meta["hashtag"] + ["#Shorts"])
            + "\n\nVideo dibuat dengan bantuan AI.")
    body = {"snippet": {"title": meta["judul"][:95], "description": desk,
                        "tags": tag, "categoryId": "27"},
            "status": {"privacyStatus": os.getenv("YT_PRIVACY", "private"),
                       "selfDeclaredMadeForKids": False}}
    req = yt.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(str(path), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]
