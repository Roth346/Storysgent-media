#!/usr/bin/env python3
"""Safe local-only vertical clipper: no downloads, publishing or account access."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import shutil
import subprocess
from pathlib import Path

MAX_DURATION = 60.0


def metadata(source: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height", "-of", "json", str(source)
    ], check=True, capture_output=True, text=True, timeout=30)
    data = json.loads(result.stdout)
    if not any(stream.get("codec_type") == "video" for stream in data.get("streams", [])):
        raise ValueError("Source does not contain video")
    if not data.get("format", {}).get("duration"):
        raise ValueError("Cannot determine source duration")
    return data


def build_command(source: Path, output: Path, start: float, duration: float,
                  height: int = 1920, fit: str = "crop") -> list[str]:
    width = height * 9 // 16
    if fit == "crop":
        vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps=30,format=yuv420p"
    else:
        vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=30,format=yuv420p"
    return [
        "ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-n",
        "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{duration:.3f}",
        "-map", "0:v:0", "-map", "0:a:0?",
        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-threads", "2", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", str(output)
    ]


def clip(source: Path, output: Path, start: float, duration: float, height: int,
         fit: str, rights_confirmed: bool, rights_notes: str) -> Path:
    if not rights_confirmed:
        raise ValueError("Rights confirmation required: --rights-confirmed")
    for program in ("ffmpeg", "ffprobe"):
        if not shutil.which(program):
            raise RuntimeError(f"Missing dependency: {program}")
    if not source.is_file():
        raise FileNotFoundError(f"Source not found: {source}")
    if source.resolve() == output.resolve():
        raise ValueError("Source and output cannot be the same file")
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output must be .mp4")
    if output.exists() or output.with_suffix(".json").exists():
        raise FileExistsError("Refusing to overwrite MP4 or metadata")
    if start < 0 or not (0 < duration <= MAX_DURATION):
        raise ValueError("Clip must begin at 0+ and last 1–60 seconds")
    if height not in (640, 1280, 1920):
        raise ValueError("Height must be 640, 1280 or 1920")
    if fit not in ("crop", "pad"):
        raise ValueError("Fit must be crop or pad")
    data = metadata(source)
    source_seconds = float(data["format"]["duration"])
    if start + duration > source_seconds + 0.1:
        raise ValueError("Clip extends past the end of the source")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            build_command(source, output, start, duration, height, fit),
            check=True, capture_output=True, text=True, timeout=900
        )
        sidecar = {
            "status": "created_not_published",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "source_filename": source.name,
            "source_duration_seconds": source_seconds,
            "start_seconds": start,
            "clip_duration_seconds": duration,
            "format": f"{height * 9 // 16}x{height}",
            "fit": fit,
            "rights_confirmed_by_operator": True,
            "rights_notes": rights_notes,
            "upload_authorized": False
        }
        output.with_suffix(".json").write_text(json.dumps(sidecar, indent=2))
        return output
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description="Clip rights-cleared local video to vertical 9:16 MP4.")
    parser.add_argument("--source", type=Path, required=True, help="Local video file, not a URL")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float, default=30)
    parser.add_argument("--height", type=int, choices=[640, 1280, 1920], default=1920)
    parser.add_argument("--fit", choices=["crop", "pad"], default="crop")
    parser.add_argument("--rights-confirmed", action="store_true", help="I have permission to repurpose this video")
    parser.add_argument("--rights-notes", default="", help="How footage is owned/licensed")
    args = parser.parse_args()
    print(clip(args.source, args.output, args.start, args.duration,
               args.height, args.fit, args.rights_confirmed, args.rights_notes))


if __name__ == "__main__":
    main()
