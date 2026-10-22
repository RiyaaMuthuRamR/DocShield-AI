import cv2


def perform_ela(image_path, quality=90):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image could not be loaded")

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]

    success, encoded_image = cv2.imencode(".jpg", image, encode_param)

    if not success:
        raise ValueError("Image encoding failed")

    recompressed = cv2.imdecode(encoded_image, cv2.IMREAD_COLOR)

    ela_image = cv2.absdiff(image, recompressed)

    return ela_image