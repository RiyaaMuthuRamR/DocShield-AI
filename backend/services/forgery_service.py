from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, UnidentifiedImageError
import numpy as np

from .storage_service import HEATMAPS_DIR, TEMP_DIR

def perform_ela(image_path: str | Path) -> tuple[str, float]:
    """Create an ELA visualization and return a heuristic indicator (0-100).

    This score is not a calibrated probability and ELA alone cannot prove forgery.
    """
    image_path = Path(image_path)
    try:
        original = Image.open(image_path).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Could not read the uploaded image for ELA analysis.") from exc

    temp_path = TEMP_DIR / f"{image_path.stem}_recompressed.jpg"
    original.save(temp_path, "JPEG", quality=90)
    compressed = Image.open(temp_path).convert("RGB")
    difference = ImageChops.difference(original, compressed)
    max_diff = max(channel[1] for channel in difference.getextrema())
    scale = 1.0 if max_diff == 0 else 255.0 / max_diff
    heatmap = ImageEnhance.Brightness(difference).enhance(scale)
    heatmap_path = HEATMAPS_DIR / f"{image_path.stem}_ela.png"
    heatmap.save(heatmap_path, format="PNG")

    gray = np.asarray(heatmap.convert("L"))
    indicator = round(float((gray > 60).sum() / gray.size * 100), 2)
    return str(heatmap_path), indicator

def analyze_document(image_path: str | Path) -> dict:
    heatmap_path, indicator = perform_ela(image_path)
    if indicator < 5:
        level = "LOW INDICATOR"
    elif indicator < 15:
        level = "MEDIUM INDICATOR"
    else:
        level = "HIGH INDICATOR"
    return {
        "heatmap_path": heatmap_path,
        "confidence": indicator,
        "risk_level": level,
        "reasons": ["ELA recompression analysis completed; review the heatmap manually."],
        "disclaimer": "This heuristic indicator is not a probability of forgery and cannot establish authenticity by itself."
    }
