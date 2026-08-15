import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple

def check_image_quality(
    image_bgr: np.ndarray,
    blur_threshold: float = 50.0,
    darkness_threshold: float = 40.0
) -> Dict[str, Any]:
    """
    Performs image quality assessment:
    1. Blur detection (Laplacian variance)
    2. Darkness detection (Mean pixel intensity)
    3. Tyre visibility check (Edge contrast analysis)
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Blur Detection (Variance of Laplacian)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurred = laplacian_var < blur_threshold

    # 2. Darkness Detection (Mean brightness)
    mean_brightness = float(gray.mean())
    is_too_dark = mean_brightness < darkness_threshold

    # 3. Tyre Visibility Check (Edge density ratio)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0) / edges.size)
    is_tyre_visible = edge_density > 0.02

    # Determine Quality Status & Quality Warning
    warnings = []
    if is_blurred:
        warnings.append(f"Image is blurred (Laplacian variance: {laplacian_var:.1f} < threshold {blur_threshold})")
    if is_too_dark:
        warnings.append(f"Image is too dark (Mean brightness: {mean_brightness:.1f} < threshold {darkness_threshold})")
    if not is_tyre_visible:
        warnings.append("Tyre structure not clearly visible in frame")

    if warnings:
        quality_status = "poor"
        quality_warning = "QUALITY WARNING: " + "; ".join(warnings)
    else:
        quality_status = "good"
        quality_warning = None

    return {
        "quality_status": quality_status,
        "is_valid": len(warnings) == 0,
        "quality_warning": quality_warning,
        "metrics": {
            "blur_score": round(laplacian_var, 1),
            "brightness_score": round(mean_brightness, 1),
            "edge_density": round(edge_density, 4),
            "is_blurred": is_blurred,
            "is_too_dark": is_too_dark,
            "is_tyre_visible": is_tyre_visible
        }
    }
