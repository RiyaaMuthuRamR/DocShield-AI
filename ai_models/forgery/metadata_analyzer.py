from PIL import Image


def analyze_metadata(image_path):
    image = Image.open(image_path)

    metadata = image.getexif()

    return {
        "format": image.format,
        "width": image.width,
        "height": image.height,
        "metadata_found": len(metadata) > 0
    }