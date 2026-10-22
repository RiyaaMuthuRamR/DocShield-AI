import cv2


def validate_qr(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image could not be loaded")

    detector = cv2.QRCodeDetector()

    data, points, _ = detector.detectAndDecode(image)

    if data:
        return {
            "valid": True,
            "data": data
        }

    return {
        "valid": False,
        "data": None
    }