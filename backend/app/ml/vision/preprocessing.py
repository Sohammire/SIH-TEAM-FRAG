import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Union

def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decodes raw image bytes into OpenCV BGR numpy array.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("Invalid image bytes - unable to decode image.")
    return img_bgr

def preprocess_image(
    image: Union[np.ndarray, Image.Image],
    target_size: Tuple[int, int] = (640, 640)
) -> Tuple[np.ndarray, np.ndarray, Image.Image]:
    """
    Resizes and normalizes image for YOLO model input.
    Returns: (img_resized_bgr, img_normalized_rgb, pil_image)
    """
    if isinstance(image, Image.Image):
        pil_img = image.convert("RGB")
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    else:
        img_bgr = image
        pil_img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    # Resize image preserving aspect ratio
    h, w = img_bgr.shape[:2]
    img_resized = cv2.resize(img_bgr, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Normalize RGB (0-1 float)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_normalized = img_rgb.astype(np.float32) / 255.0

    return img_resized, img_normalized, pil_img
