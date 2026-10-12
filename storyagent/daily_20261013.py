"""Original StoryAgent photo stories for 2026-10-13 (Europe/London)."""
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

STORIES = {
    "animal": {
        "title": "THE 8:10 TRAIN",
        "genre": "AN EMOTIONAL ANIMAL STORY",
        "bg": (17, 41, 54), "accent": (244, 179, 112),
        "slides": [
            "Every morning, a stray dog waited for the 8:10 train.",
            "He carried the same faded red scarf in his mouth.",
            "The station porter checked the name sewn inside: MILO.",
            "She posted a photo. A woman replied within minutes.",
            "I made that scarf for my father. Milo was his dog.",
            "Her father was gone. But Milo kept their routine. Now he finally had someone to go home with."
        ]
    },
    "mystery": {
        "title": "THE 11:11 DOOR",
        "genre": "A MYSTERY WITH A TWIST",
        "bg": (31, 29, 57), "accent": (175, 159, 244),
        "slides": [
            "Every night at 11:11, the museum's locked door swung open.",
            "The night guard checked the cameras. Nobody touched it.",
            "He changed the lock. At 11:11, it happened again.",
            "Then he noticed the floor trembled just before it opened.",
            "He followed the vibration to the railway tunnel below.",
            "The last train passed at 11:11. The doorframe was dangerously loose. The ghost had been a warning."
        ]
    },
    "kindness": {
        "title": "THE YELLOW UMBRELLA",
        "genre": "A STORY ABOUT KINDNESS",
        "bg": (32, 48, 48), "accent": (249, 211, 95),
        "slides": [
            "A woman left a yellow umbrella at a bus stop with a note.",
            "Take me if you need me. Leave me for someone else.",
            "A student borrowed it on the way to an important exam.",
            "A cleaner used it to walk home through a storm.",
            "Weeks later, the umbrella returned to the same bus stop.",
            "A new note hung from its handle: You kept six strangers dry. Thank you."
        ]
    }
}

def font(size, bold=False):
    names = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)

def wrap(draw, text, f, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if line and draw.textbbox((0, 0), trial, font=f)[2] > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines

def jpeg_for(slug, slide):
    if slug not in STORIES or not (1 <= slide <= 6):
        raise ValueError("Unknown media")
    data = STORIES[slug]
    image = Image.new("RGB", (1080, 1920), data["bg"])
    d = ImageDraw.Draw(image)
    accent = data["accent"]
    d.rounded_rectangle((65, 75, 1015, 1845), radius=48, outline=accent, width=5)
    d.text((120, 145), "STORYAGENT  /  ORIGINAL FICTION", font=font(29, True), fill=accent)
    d.line((120, 225, 960, 225), fill=accent, width=3)
    d.text((120, 295), data["title"], font=font(54, True), fill="white")
    d.rounded_rectangle((120, 480, 960, 900), radius=40, outline=accent, width=5)
    d.text((420, 520), f"{slide:02}", font=font(240, True), fill=accent)
    d.rounded_rectangle((110, 980, 970, 1550), radius=38, fill=(247, 242, 228))
    txt = data["slides"][slide - 1]
    for size in range(62, 37, -2):
        f = font(size, True)
        lines = wrap(d, txt, f, 730)
        spacing = int(size * 1.45)
        if len(lines) * spacing <= 450:
            break
    y = 1060 + (430 - len(lines) * spacing) // 2
    for line in lines:
        d.text((170, y), line, font=f, fill=(26, 32, 39))
        y += spacing
    d.text((120, 1660), data["genre"], font=font(29, True), fill=accent)
    d.text((120, 1740), "SWIPE FOR MORE  >" if slide < 6 else "FOLLOW FOR MORE STORIES", font=font(30, True), fill="white")
    d.text((870, 1740), f"{slide}/6", font=font(30, True), fill=accent)
    out = BytesIO()
    image.save(out, format="JPEG", quality=88, optimize=True)
    return out.getvalue()
