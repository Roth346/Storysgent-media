"""Generate three original fictional TikTok photo stories daily.
Images are local JPEGs until uploaded with cloudinary_upload.upload_photo.
"""
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

STORIES = [
    ("The Dog With One Leaf", [
        "Every morning, a stray dog waited outside the flower shop.",
        "He never begged for food. He carried one fallen leaf.",
        "One rainy day, the shopkeeper followed him.",
        "He led her to a tiny garden beside an empty house.",
        "There, a handwritten sign read: 'For anyone who needs a friend.'",
        "She opened the garden gate. The dog finally went inside."
    ], "A small kindness can open a door. Fictional story, AI-assisted. #storytime #dogstory #kindness"),
    ("The House in the Photo", [
        "Mara bought an old camera at a market.",
        "Every picture developed with the same house in the background.",
        "Even photos taken miles away showed its blue front door.",
        "She found the address written inside the camera case.",
        "At the house, an elderly woman opened the door and smiled.",
        "'You found my husband's camera,' she said. 'He always photographed home.'"
    ], "Some mysteries have gentle endings. Fictional story, AI-assisted. #mystery #storytime #plotwist"),
    ("The Book at the Bus Stop", [
        "Every Friday, someone left a book at the bus stop.",
        "Inside each cover was a note: 'Take what you need today.'",
        "One week, the books stopped appearing.",
        "The commuters left their own books, each with a note.",
        "By winter, the bench had become a little free library.",
        "Nobody knew who began it. Everyone knew why it continued."
    ], "A good idea can travel further than its creator. Fictional story, AI-assisted. #inspiration #shortstory #kindness")
]

def font(size):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

def create_cards(folder="storyagent/output"):
    root = Path(folder) / datetime.now().strftime("%Y-%m-%d")
    result = []
    for index, (title, slides, caption) in enumerate(STORIES, 1):
        files = []
        for number, words in enumerate(slides, 1):
            img = Image.new("RGB", (1080, 1440), (23 + index * 7, 28 + index * 4, 42 + index * 3))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle((72, 110, 1008, 1330), radius=42, outline=(216, 184, 126), width=5)
            draw.text((125, 185), title, font=font(48), fill=(245, 217, 161))
            y = 420
            for line in textwrap.wrap(words, 31):
                draw.text((125, y), line, font=font(51), fill="white")
                y += 86
            draw.text((125, 1190), f"{number} / {len(slides)}   •   FICTION", font=font(29), fill=(200, 202, 210))
            path = root / f"story-{index:02d}-slide-{number:02d}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            img.save(path, "JPEG", quality=88, optimize=True)
            files.append(str(path))
        result.append({"title":title,"caption":caption,"files":files})
    return result

if __name__ == "__main__":
    for item in create_cards():
        print(item["title"], len(item["files"]), "JPEGs generated")
