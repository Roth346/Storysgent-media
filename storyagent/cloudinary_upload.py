"""Upload JPEG/WebP files to Cloudinary using credentials from CLOUDINARY_URL."""
import os
from pathlib import Path
import cloudinary
import cloudinary.uploader
from PIL import Image


def upload_photo(path: str) -> str:
    if not os.getenv('CLOUDINARY_URL'):
        raise RuntimeError('Missing CLOUDINARY_URL in Render environment')
    file = Path(path)
    if file.suffix.lower() not in {'.jpg', '.jpeg', '.webp'}:
        raise ValueError('TikTok photo must be JPEG or WebP')
    with Image.open(file) as im:
        if im.format not in {'JPEG', 'WEBP'}:
            raise ValueError('File content must be JPEG or WebP')
    cloudinary.config(cloud_name='oe5bvdqa', secure=True)
    result = cloudinary.uploader.upload(str(file), folder='storyagent/tiktok', resource_type='image', overwrite=False, unique_filename=True)
    url = result.get('secure_url')
    if not url or not url.startswith('https://'):
        raise RuntimeError('Cloudinary did not return secure_url')
    return url
