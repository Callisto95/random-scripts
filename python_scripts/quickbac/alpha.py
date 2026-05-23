from PySide6.QtGui import QColor, QImage

NO_ALPHA: int = 255
ALPHA_THRESHOLD: int = 5
FALLBACK_BACKGROUND_COLOUR: QColor = QColor(0x33, 0x33, 0x33)


def get_colour(image: QImage, x: int, y: int) -> QColor:
    colour: QColor = image.pixelColor(x, y)
    
    if colour.alpha() <= ALPHA_THRESHOLD and colour.red() == 0 and colour.green() == 0 and colour.blue() == 0:
        return FALLBACK_BACKGROUND_COLOUR
    
    colour.setAlpha(NO_ALPHA)
    
    return colour


def is_alpha(image: QImage) -> bool:
    return image.pixelColor(0, 0).alpha() != NO_ALPHA
