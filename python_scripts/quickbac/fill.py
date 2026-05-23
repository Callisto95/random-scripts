from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QColorSpace, QImage, QPainter

from python_scripts.quickbac.alpha import get_colour
from python_scripts.quickbac.data import compute_dimensions, ImageModifier, Modification, Offsets, RatioSelector


class Filler(ImageModifier):
    def __init__(self, ratio: RatioSelector, horizontal: bool):
        self.horizontal: bool = horizontal
        self.ratio: RatioSelector = ratio
    
    def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
        location: Modification = compute_dimensions(current_image, self.ratio.current_ratio(), offsets, False)
        
        base_image: QImage = QImage(QSize(location.target_width, location.target_height), current_image.format())
        base_image.setColorSpace(
            current_image.colorSpace()
            if current_image.colorSpace().isValid()
            else QColorSpace.NamedColorSpace.SRgb,
        )
        
        painter: QPainter = QPainter(base_image)
        
        if self.horizontal:
            left_colour: QColor = get_colour(current_image, 0, 0)
            right_colour: QColor = get_colour(current_image, current_image.width() - 1, 0)
            painter.fillRect(QRect(0, 0, location.target_width, location.target_height), right_colour)
            painter.fillRect(
                QRect(0, 0, round(location.x_offset + current_image.width() / 2), location.target_height),
                left_colour,
            )
        else:
            upper_colour: QColor = get_colour(current_image, 0, 0)
            lower_colour: QColor = get_colour(current_image, 0, current_image.height() - 1)
            painter.fillRect(QRect(0, 0, location.target_width, location.target_height), lower_colour)
            painter.fillRect(
                QRect(0, 0, location.target_width, round(location.y_offset + current_image.height() / 2)),
                upper_colour,
            )
        
        painter.drawImage(location.x_offset, location.y_offset, current_image)
        painter.end()
        
        return base_image
