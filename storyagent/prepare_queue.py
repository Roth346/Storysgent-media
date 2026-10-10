"""StoryAgent daily media preparation. Requires CLOUDINARY_URL in Render environment.
Generates three six-slide JPEG carousels and uploads them to Cloudinary.
Writes a JSON queue for Metricool scheduling; never posts without a verified scheduler.
"""
import json
from datetime import datetime
from pathlib import Path
from generate_stories import create_cards
from cloudinary_upload import upload_photo

def prepare():
    queue = []
    for story in create_cards():
        urls = [upload_photo(p) for p in story["files"]]
        queue.append({"title": story["title"], "caption": story["caption"], "media": urls,
                      "network": "tiktok", "autoPublish": True})
    out = Path("storyagent/output") / f"queue-{datetime.now():%Y-%m-%d}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(queue, indent=2))
    print(f"Prepared {len(queue)} stories; queue saved at {out}")
    return queue

if __name__ == "__main__":
    prepare()
