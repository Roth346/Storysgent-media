#!/usr/bin/env python3
"""Turn an existing ORIGINAL StoryAgent text story into a review-only vertical MP4."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "storyagent"))


def font(size: int):
    for name in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def wrap(draw, words: str, f, max_width: int):
    lines, current = [], ""
    for word in words.split():
        candidate = (current + " " + word).strip()
        if current and draw.textbbox((0, 0), candidate, font=f)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def slide_image(title: str, sentence: str, number: int, total: int, dest: Path):
    W, H = 720, 1280
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        r = y / H
        d.line((0, y, W, y), fill=(int(14 + 13 * r), int(25 + 5 * r), int(49 + 15 * r)))
    d.ellipse((-180, -180, 330, 340), fill=(25, 44, 78))
    d.ellipse((390, 925, 940, 1500), outline=(65, 90, 134), width=4)
    d.rounded_rectangle((46, 80, 674, 1136), radius=34, outline=(241, 193, 115), width=3)
    d.text((75, 126), "STORYAGENT / ORIGINAL STORY", fill=(241, 193, 115), font=font(24))
    d.line((75, 200, 645, 200), fill=(241, 193, 115), width=3)
    y = 260
    title_font = font(46)
    for line in wrap(d, title.upper(), title_font, 545):
        d.text((75, y), line, font=title_font, fill=(252, 244, 225))
        y += 65
    body_font = font(41)
    lines = wrap(d, sentence, body_font, 540)
    while len(lines) > 8 and body_font.size > 29:
        body_font = font(body_font.size - 2)
        lines = wrap(d, sentence, body_font, 540)
    y = 550 + max(0, (350 - len(lines) * 62) // 2)
    for line in lines:
        d.text((75, y), line, font=body_font, fill="white")
        y += 62
    d.rounded_rectangle((75, 1060, 645, 1066), radius=3, fill=(52, 75, 106))
    d.rounded_rectangle((75, 1060, 75 + int(570 * number / total), 1066), radius=3, fill=(241, 193, 115))
    d.text((75, 1100), f"{number} / {total}  •  FICTION", font=font(24), fill=(241, 193, 115))
    im.save(dest)


def make_video(out: Path, story_index: int = 1, voice: bool = True):
    from generate_stories import STORIES
    for tool in ["ffmpeg", "ffprobe"] + (["espeak"] if voice else []):
        if not shutil.which(tool):
            raise RuntimeError(f"Missing prerequisite: {tool}")
    if out.exists() or out.with_suffix(".json").exists():
        raise FileExistsError(f"Refusing to overwrite output: {out}")
    if not (1 <= story_index <= len(STORIES)):
        raise ValueError(f"Story index must be 1..{len(STORIES)}")
    title, sentences, caption = STORIES[story_index - 1]
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        videos = []
        for i, sentence in enumerate(sentences, 1):
            img = tmp / f"card{i:02d}.png"
            slide_image(title, sentence, i, len(sentences), img)
            duration, wav = 4.0, None
            if voice:
                wav = tmp / f"voice{i:02d}.wav"
                subprocess.run(["espeak", "-v", "en-gb", "-s", "145", "-w", str(wav), sentence],
                               check=True, capture_output=True, timeout=30)
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(wav)],
                    check=True, capture_output=True, text=True, timeout=30)
                duration = max(3.5, float(result.stdout.strip()) + 0.65)
            segment = tmp / f"scene{i:02d}.mp4"
            command = ["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y",
                       "-loop", "1", "-framerate", "24", "-i", str(img)]
            if voice:
                command += ["-i", str(wav), "-filter_complex",
                            f"[1:a]apad=whole_dur={duration:.3f}[aud]",
                            "-map", "0:v:0", "-map", "[aud]", "-c:a", "aac", "-b:a", "96k"]
            command += ["-t", f"{duration:.3f}", "-vf", "format=yuv420p", "-c:v", "libx264",
                        "-preset", "ultrafast", "-crf", "29", "-r", "24", "-threads", "2", str(segment)]
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=150)
            videos.append(segment)
        manifest = tmp / "scenes.txt"
        manifest.write_text("".join(f"file '{p.as_posix()}'\n" for p in videos))
        subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-y", "-f", "concat",
                        "-safe", "0", "-i", str(manifest), "-c", "copy", "-movflags", "+faststart",
                        str(out)], check=True, capture_output=True, text=True, timeout=150)
    out.with_suffix(".json").write_text(json.dumps({
        "title": title, "caption": caption, "source": "StoryAgent original fictional story",
        "status": "preview_only_not_published", "upload_authorized": False,
        "synthetic_voice": voice, "output": out.name}, indent=2))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--story", type=int, default=1)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--no-voice", action="store_true")
    a = p.parse_args()
    print(make_video(a.output, a.story, voice=not a.no_voice))


if __name__ == "__main__":
    main()
