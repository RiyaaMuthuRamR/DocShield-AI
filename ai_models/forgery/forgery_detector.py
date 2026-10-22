import cv2
import numpy as np

from ai_models.forgery.ela import perform_ela
from ai_models.forgery.evidence import create_evidence


def detect_forgery(image_path):
    """
    Analyze a document image for possible forgery.

    ELA is used as one supporting signal.
    ELA alone does NOT prove that a document is forged.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image could not be loaded")

    # ---------------------------------------------
    # Basic image analysis
    # ---------------------------------------------

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    mean_value = float(np.mean(gray))
    std_value = float(np.std(gray))

    # ---------------------------------------------
    # Error Level Analysis
    # ---------------------------------------------

    ela_image = perform_ela(image_path)

    ela_mean = float(np.mean(ela_image))

    # ---------------------------------------------
    # Evidence
    # ---------------------------------------------

    evidence = []

    # Existing image variation signal
    if std_value > 80:
        evidence.append(
            "High image intensity variation"
        )

    # ELA signal
    if ela_mean > 10:
        evidence.append(
            "Elevated Error Level Analysis signal"
        )

    # ---------------------------------------------
    # Conservative decision
    # ---------------------------------------------
    #
    # ELA alone should not mark a document as forged.
    # We only flag it when multiple suspicious
    # signals are present.

    suspicious_signals = 0

    if std_value > 80:
        suspicious_signals += 1

    if ela_mean > 10:
        suspicious_signals += 1

    tampered = suspicious_signals >= 2

    # ---------------------------------------------
    # Confidence
    # ---------------------------------------------

    confidence = min(
        (
            (std_value / 100) +
            (ela_mean / 100)
        ) / 2,
        1.0
    )

    return create_evidence(
        tampered,
        round(confidence, 2),
        evidence
    )