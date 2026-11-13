# yt_upload — upload a video to YouTube from the terminal

One file (`yt_upload.py`), the official YouTube Data API v3. It uploads one video, **private by default**, and can read the title and description straight from a Neryn posting kit (`POSTING_EPNN.md`).

## 1. One-time setup (about 10 minutes, on your own computer)

1. Go to <https://console.cloud.google.com/>, create a project (any name, e.g. `neryn-uploader`).
2. **APIs & Services → Library →** search **YouTube Data API v3 → Enable**.
3. **APIs & Services → OAuth consent screen:** User type **External**, fill the app name and your email, leave it in **Testing**, and under **Test users** add the Google account that owns the YouTube channel.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID → Application type: Desktop app.** Download the JSON and save it as `client_secret.json` next to `yt_upload.py`. Treat it like a password: never commit it (the `.gitignore` here already blocks it).
5. Install the libraries and sign in:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python3 yt_upload.py auth
   ```
   A browser opens. Choose the Google account, then the channel. A token is saved to `~/.config/neryn-yt/token.json` (readable only by you).

## 2. Upload

Look first, upload second:
```bash
python3 yt_upload.py upload ep02-clinic-v4.mp4 --kit POSTING_EP02_CLINIC.md --title-pick 1 --dry-run
python3 yt_upload.py upload ep02-clinic-v4.mp4 --kit POSTING_EP02_CLINIC.md --title-pick 1
```
The first command prints exactly what would be sent and uploads nothing. The second uploads and prints the video link and the Studio link.

Useful options:

| Option | What it does |
|---|---|
| `--kit FILE --title-pick N` | Takes title option N and the description from the kit's `## YouTube Shorts` section |
| `--title`, `--description`, `--description-file` | Use these instead of a kit |
| `--privacy private\|unlisted\|public` | Default `private` |
| `--publish-at 2026-11-14T19:30:00+05:30` | Upload private now, YouTube makes it public at that time (7–9 PM IST is the best slot) |
| `--thumbnail cover.png` | Sets a custom thumbnail (needs a phone-verified channel; Shorts mostly show a video frame) |
| `--shorts` | Adds `#Shorts` to the description |
| `--not-synthetic` | Turns **off** the "altered or synthetic content" flag. It is on by default because Neryn voices are AI |
| `--tags a,b,c` | Default: the `#hashtags` in the description |

Every upload is also marked "not made for kids".

## 3. Why is my upload private? (read this before you rely on it)

Google locks videos uploaded through the API to **private** when the Google Cloud project was created after 28 July 2020 and has not passed Google's **YouTube API Services audit**. A brand-new project like the one in step 1 is in that state. Google's help says a video locked this way **cannot be appealed**; the fix is to upload it again through the YouTube app/website or through an audited API project.

What to do:
- **Right now:** use this CLI for private test uploads. For any video that must go public, upload it with the YouTube app or Studio, as the posting kit describes. If you want to try `--publish-at`, test it on a throwaway video first and check in Studio that it is scheduled rather than locked.
- **To lift the lock:** apply for the compliance audit at <https://support.google.com/youtube/contact/yt_api_form>. It is meant for apps with real users and can take weeks. A one-channel personal tool may not be approved.

## 4. Things that will surprise you

- **Weekly sign-in.** While the consent screen is in *Testing*, Google expires the token after 7 days. Run `python3 yt_upload.py auth` again when you see "Saved sign-in expired".
- **Quota.** An upload costs 1 unit from a separate upload quota that is capped per day per project. Several uploads a day is fine; hundreds is not.
- **No pinned comments.** The API cannot pin a comment. Post and pin it by hand from the kit.
- **No private files.** Never commit `client_secret*.json` or `token*.json`.
