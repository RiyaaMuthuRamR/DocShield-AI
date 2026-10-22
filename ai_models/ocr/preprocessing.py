import cv2


def preprocess_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image could not be loaded")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray


def preprocess_mrz(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image could not be loaded")

    height, width = image.shape[:2]

    # MRZ is normally located at the bottom of the document.
    # Keep a slightly larger area so characters are not accidentally cut.
    mrz = image[int(height * 0.80):height, 0:width]

    # Convert to grayscale
    gray = cv2.cvtColor(mrz, cv2.COLOR_BGR2GRAY)

    # Upscale for OCR
    gray = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    # Reduce noise
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    # Adaptive threshold handles uneven document lighting better.
    threshold = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return threshold