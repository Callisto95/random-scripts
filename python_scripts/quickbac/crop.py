from PySide6.QtGui import QColorSpace, QImage, QPainter

from python_scripts.quickbac.alpha import FALLBACK_BACKGROUND_COLOUR, is_alpha
from python_scripts.quickbac.data import compute_dimensions, ImageModifier, Modification, Offsets, RatioSelector
from python_scripts.quickbac.ui import LOGGER


class Cropper(ImageModifier):
    def __init__(self, ratio: RatioSelector):
        self.ratio: RatioSelector = ratio
    
    def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
        location: Modification = compute_dimensions(current_image, self.ratio.current_ratio(), offsets, True)
        
        base_image: QImage = QImage(location.target_width, location.target_height, current_image.format())
        base_image.setColorSpace(
            current_image.colorSpace()
            if current_image.colorSpace().isValid()
            else QColorSpace.NamedColorSpace.SRgb,
        )
        
        if is_alpha(current_image):
            LOGGER.info("image has alpha, filling background first")
            base_image.fill(FALLBACK_BACKGROUND_COLOUR)
        
        painter: QPainter = QPainter(base_image)
        painter.drawImage(location.x_offset, location.y_offset, current_image)
        painter.end()
        
        return base_image
