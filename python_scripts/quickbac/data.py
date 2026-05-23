from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from PySide6.QtGui import QImage


@dataclass(frozen=True)
class Modification:
    target_width: int
    target_height: int
    x_offset: int
    y_offset: int


class ImageModifier(ABC):
    @abstractmethod
    def modify(self, current_image: QImage, offsets: Offsets) -> QImage:
        pass


class ImageProcessorFactory:
    def __init__(self):
        self.modifiers: dict[tuple[bool, bool], ImageModifier] = { }
    
    def register(self, horizontal: bool, crop: bool, modifier: ImageModifier) -> None:
        self.modifiers[(horizontal, crop)] = modifier
    
    def get(self, horizontal: bool, crop: bool) -> ImageModifier:
        return self.modifiers[(horizontal, crop)]


@dataclass(frozen=True)
class Offsets:
    primary: float
    secondary: float
    zoom: float


def compute_dimensions(image: QImage, ratio: float, offsets: Offsets, crop: bool) -> Modification:
    image_ratio: float = image.width() / image.height()
    
    # Crop: base on the constraining dimension
    # Fill: base on the dominant dimension
    if (image_ratio > ratio) == crop:
        height: int = round(image.height() * offsets.zoom)
        width: int = round(height * ratio)
        x_offset: int = round((width - image.width()) / 2 * offsets.primary)
        y_offset: int = round((height - image.height()) / 2 * offsets.secondary)
    else:
        width: int = round(image.width() * offsets.zoom)
        height: int = round(width / ratio)
        y_offset: int = round((height - image.height()) / 2 * offsets.primary)
        x_offset: int = round((width - image.width()) / 2 * offsets.secondary)
    
    return Modification(width, height, x_offset, y_offset)


class RatioSelector:
    def __init__(self, ratios: list[tuple[int, int]]):
        self.ratios: list[tuple[int, int]] = ratios
        self.index: int = 0
    
    def current_ratio(self) -> float:
        w, h = self.ratios[self.index]
        return w / h
    
    def current(self) -> tuple[int, int]:
        return self.ratios[self.index]
    
    def advance(self) -> tuple[int, int]:
        self.index = (self.index + 1) % len(self.ratios)
        return self.ratios[self.index]
