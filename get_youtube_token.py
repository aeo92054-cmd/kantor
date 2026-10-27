"""Jalankan SEKALI di komputermu untuk mendapat refresh token YouTube.
Butuh client_secret.json (OAuth client tipe Desktop dari Google Cloud Console)."""
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", ["https://www.googleapis.com/auth/youtube.upload"])
c = flow.run_local_server(port=0)
print("\nSimpan tiga nilai ini sebagai GitHub Secrets:")
print("YT_CLIENT_ID     =", c.client_id)
print("YT_CLIENT_SECRET =", c.client_secret)
print("YT_REFRESH_TOKEN =", c.refresh_token)
