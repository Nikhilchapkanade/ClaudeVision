import os
from PIL import Image

def convert_image_to_webp(image_path, quality=80):
    """
    Converts an image to WebP format for web optimization.
    """
    if not os.path.exists(image_path):
        return f"Error: File {image_path} not found."

    filename, _ = os.path.splitext(image_path)
    output_path = f"{filename}.webp"

    try:
        with Image.open(image_path) as img:
            img.save(output_path, "WEBP", quality=quality)
        return output_path
    except Exception as e:
        return f"Error converting image: {str(e)}"