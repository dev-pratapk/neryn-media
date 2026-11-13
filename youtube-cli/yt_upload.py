#!/usr/bin/env python3
"""Upload a video to YouTube (Shorts friendly) with the YouTube Data API v3.

    python3 yt_upload.py auth                      # one-time browser sign-in, saves a token
    python3 yt_upload.py upload VIDEO --kit POSTING_EP02_CLINIC.md --title-pick 1 --dry-run
    python3 yt_upload.py upload VIDEO --kit POSTING_EP02_CLINIC.md --title-pick 1

Defaults are the safe ones: the video is uploaded PRIVATE, marked "not made for kids" and marked
"altered or synthetic content" (Neryn episodes use AI voices). Nothing is uploaded without the
`upload` command; use --dry-run to see exactly what would be sent.
"""
import argparse
import json
import os
import random
import re
import sys
import time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CONFIG_DIR = os.path.expanduser(os.environ.get("NERYN_YT_HOME", "~/.config/neryn-yt"))
DEFAULT_TOKEN = os.path.join(CONFIG_DIR, "token.json")
DEFAULT_SECRET = os.environ.get("YT_CLIENT_SECRET", "client_secret.json")
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}


# ----------------------------------------------------------------- posting-kit parser
def read_kit(path, pick):
    """Return (title, description) from a POSTING_EPNN.md written the Neryn way.

    Looks inside the "## YouTube Shorts" section for the numbered list under "Title options" and
    the first fenced block under "Description".
    """
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^## YouTube Shorts\s*$(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    if not m:
        sys.exit(f"{path}: no '## YouTube Shorts' section found")
    sec = m.group(1)
    titles = re.findall(r"^\s*\d+\.\s+(.+?)\s*$", sec.split("**Description**")[0], flags=re.M)
    if not titles:
        sys.exit(f"{path}: no numbered title options found")
    if not 1 <= pick <= len(titles):
        sys.exit(f"--title-pick must be 1..{len(titles)}")
    d = re.search(r"\*\*Description\*\*\s*```[^\n]*\n(.*?)```", sec, flags=re.S)
    if not d:
        sys.exit(f"{path}: no fenced Description block found")
    return titles[pick - 1], d.group(1).strip()


def tags_from_description(desc):
    return [t.lstrip("#") for t in re.findall(r"#\w+", desc)][:15]


# ----------------------------------------------------------------- request body
def build_body(args, title, description):
    if len(title) > 100:
        sys.exit(f"Title is {len(title)} characters; YouTube allows 100.")
    if len(description.encode("utf-8")) > 5000:
        sys.exit("Description is over YouTube's 5000-byte limit.")
    if args.shorts and "#shorts" not in description.lower():
        description = description.rstrip() + "\n#Shorts"
    tags = [t.strip().lstrip("#") for t in args.tags.split(",") if t.strip()] if args.tags else tags_from_description(description)
    while sum(len(t) + 1 for t in tags) > 480:  # API limit is 500 characters in total
        tags.pop()
    status = {
        "privacyStatus": args.privacy,
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": not args.not_synthetic,
    }
    if args.publish_at:
        if args.privacy != "private":
            sys.exit("--publish-at needs --privacy private (YouTube publishes it at that time).")
        status["publishAt"] = args.publish_at
    return {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": args.category,
                    "defaultLanguage": args.language, "defaultAudioLanguage": args.language},
        "status": status,
    }


# ----------------------------------------------------------------- google client
def load_credentials(token_path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    if not os.path.exists(token_path):
        sys.exit(f"No saved sign-in at {token_path}. Run:  python3 yt_upload.py auth")
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_token(creds, token_path)
        else:
            sys.exit("Saved sign-in expired. Run:  python3 yt_upload.py auth")
    return creds


def save_token(creds, token_path):
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    fd = os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(creds.to_json())


def cmd_auth(args):
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not os.path.exists(args.client_secret):
        sys.exit(f"{args.client_secret} not found. Download the OAuth *Desktop app* client JSON from Google Cloud "
                 "console (APIs & Services → Credentials) and pass it with --client-secret.")
    flow = InstalledAppFlow.from_client_secrets_file(args.client_secret, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    save_token(creds, args.token)
    print(f"Signed in. Token saved to {args.token} (readable only by you).")
    print("Uploads go to the YouTube channel you picked on the Google consent screen.")


def resumable_upload(request):
    import httplib2
    from googleapiclient.errors import HttpError
    response, retry = None, 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"  uploaded {int(status.progress() * 100)}%", end="\r", flush=True)
        except HttpError as e:
            if e.resp.status not in (500, 502, 503, 504):
                raise
            retry = backoff(retry, f"HTTP {e.resp.status}")
        except (OSError, httplib2.HttpLib2Error) as e:
            retry = backoff(retry, type(e).__name__)
    print("  uploaded 100%      ")
    return response


def backoff(retry, why):
    retry += 1
    if retry > 8:
        sys.exit(f"Giving up after repeated errors ({why}).")
    wait = min(60, 2 ** retry) + random.random()
    print(f"  {why}; retrying in {wait:.0f}s", file=sys.stderr)
    time.sleep(wait)
    return retry


def cmd_upload(args):
    video = args.video
    if not os.path.isfile(video) or os.path.splitext(video)[1].lower() not in VIDEO_EXT:
        sys.exit(f"{video}: not a video file")
    if args.kit:
        title, description = read_kit(args.kit, args.title_pick)
        title = args.title or title
        description = open(args.description_file, encoding="utf-8").read().strip() if args.description_file else description
    else:
        if not args.title:
            sys.exit("Give --title (or use --kit).")
        title = args.title
        description = open(args.description_file, encoding="utf-8").read().strip() if args.description_file else (args.description or "")
    body = build_body(args, title, description)

    print(f"File:     {video} ({os.path.getsize(video) / 1e6:.1f} MB)")
    print(f"Title:    {body['snippet']['title']}")
    print(f"Privacy:  {body['status']['privacyStatus']}" + (f" → public at {body['status']['publishAt']}" if args.publish_at else ""))
    print(f"AI/synthetic content flag: {body['status']['containsSyntheticMedia']}   Made for kids: False")
    if args.dry_run:
        print("\n--dry-run: nothing was uploaded. Request body:\n" + json.dumps(body, ensure_ascii=False, indent=2))
        return

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    youtube = build("youtube", "v3", credentials=load_credentials(args.token))
    media = MediaFileUpload(video, chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    result = resumable_upload(request)
    vid = result["id"]
    print(f"\nUploaded: https://youtube.com/shorts/{vid}")
    print(f"Studio:   https://studio.youtube.com/video/{vid}/edit")
    if args.thumbnail:
        youtube.thumbnails().set(videoId=vid, media_body=MediaFileUpload(args.thumbnail)).execute()
        print("Thumbnail set (needs a phone-verified channel; Shorts mostly show the video frame anyway).")
    if body["status"]["privacyStatus"] != "private" and result.get("status", {}).get("privacyStatus") == "private":
        print("\nNote: YouTube kept this video PRIVATE. Uploads from API projects that have not passed Google's "
              "audit are locked private. See README → 'Why is my upload private?'.")


# ----------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("auth", help="sign in once in the browser and save a token")
    a.add_argument("--client-secret", default=DEFAULT_SECRET, help="OAuth Desktop client JSON (default: ./client_secret.json or $YT_CLIENT_SECRET)")
    a.add_argument("--token", default=DEFAULT_TOKEN)
    a.set_defaults(fn=cmd_auth)

    u = sub.add_parser("upload", help="upload one video")
    u.add_argument("video")
    u.add_argument("--kit", help="posting kit markdown (reads title options + description from '## YouTube Shorts')")
    u.add_argument("--title-pick", type=int, default=1, help="which numbered title option from the kit (default 1)")
    u.add_argument("--title")
    u.add_argument("--description")
    u.add_argument("--description-file")
    u.add_argument("--tags", help="comma separated; default: the #hashtags in the description")
    u.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    u.add_argument("--publish-at", help="RFC 3339 time to go public, e.g. 2026-11-14T19:30:00+05:30 (needs --privacy private)")
    u.add_argument("--category", default="22", help="YouTube category id (default 22, People & Blogs)")
    u.add_argument("--language", default="ta", help="video language code (default ta)")
    u.add_argument("--shorts", action="store_true", help="append #Shorts to the description")
    u.add_argument("--not-synthetic", action="store_true", help="do NOT flag the video as altered/synthetic content")
    u.add_argument("--thumbnail", help="PNG/JPG cover to set after upload")
    u.add_argument("--token", default=DEFAULT_TOKEN)
    u.add_argument("--dry-run", action="store_true", help="print the request and stop; no network, no sign-in needed")
    u.set_defaults(fn=cmd_upload)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
