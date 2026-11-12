# Shorts Clipper V1 — review-only staging

Local video pipeline for YouTube Shorts and TikTok previews, without paid APIs or social account access.

## What is ready

- `shorts/clipper.py`: cut an owned or properly licensed local source video into vertical 9:16 MP4 at 360x640, 720x1280 or 1080x1920. Centre-crop or letterbox, preserve existing audio, and write an audit sidecar. Explicit rights confirmation is required. Limit: 60 seconds.
- `shorts/story_short.py`: generate a video from one of the **existing original fictional stories** in `storyagent/generate_stories.py`; renders readable vertical cards, simple progress markers and optional local synthetic narration.
- Preview only: NO posting, account logins, searching/downloading viral video, paid APIs, scheduling or server deployment.

## Run original story Short

Prerequisites: Python 3.10+, Pillow (`python3 -m pip install Pillow`), `ffmpeg`, `ffprobe`, and `espeak` for voice.

From repository root:

```sh
python3 shorts/story_short.py --story 1 --output output/story01.mp4
```

Use `--story 2` or `--story 3` for the other original stories. For a silent video, pass `--no-voice` (synthetic narration will be absent). The renderer creates `.mp4` and a `.json` metadata file. It never publishes.

## Trim your own/licensed footage into a Short

```sh
python3 shorts/clipper.py --source /path/to/owned.mp4 --start 15 --duration 30 \
  --output output/short01.mp4 --rights-confirmed --rights-notes "Original footage I recorded"
```

Change `--fit pad` for no centre crop and `--height 1280` for a 720x1280 render (default is 1080x1920). This release is local-file-only. If using another person's video, confirm that the specific licence or written permission covers editing **and** redistribution on the intended platforms. Do not infer rights just because a video is public.

## Verification

```sh
python3 -m unittest discover -s tests -p 'test_clipper.py' -v
ffprobe -v error -show_entries stream=codec_name,width,height -show_entries format=duration -of json output/story01.mp4
```

Local validation before PR: 3 unit tests pass, actual first story preview rendered in 720x1280 MP4 with H.264/AAC, and a 10-second cut of that generated MP4 rendered to 360x640 retaining video and audio. Two further original story previews rendered. **These tests ran in a separate local environment, not on the Hermes 5 server**. GitHub CI, Contabo, account publishing, persistent queue, clip detection, and full autonomous operation are **NOT VERIFIED**.

## Security and next steps

Only local, rights-cleared videos. No third-party platform scraping; no copying cookies or account data; no automated publication, monetisation, or customer outreach. Retain permission records with outputs. Do not use the released StoryAgent scripts' autoPublish queue unless separately authorised and its integration tested. Future work: proper word-level captions, subject-aware reframing, licensed-source intake, task queue, review/approval dashboard, and official publishing integrations.

The currently accessible GitHub account has no Hermes 5 repository; this implementation is staged in the existing StoryAgent media repository as a standalone candidate. It does **not** change Hermes 1, 2 or 3.
