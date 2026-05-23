from argparse import ArgumentParser, Namespace
from math import floor, sqrt
from pathlib import Path

from PIL import Image as Img
from PIL.Image import Image

from python_scripts.logger import Logger

LOGGER: Logger = Logger("FA-U")

MAX_RESOLUTION: tuple[int, int] = (2560, 1440)
MAX_PIXELS: int = MAX_RESOLUTION[0] * MAX_RESOLUTION[1]

EXPORT_FOLDER: Path = Path("fa-upload")


def export_image(image: Image, image_file: Path) -> Path:
    EXPORT_FOLDER.mkdir(exist_ok=True, parents=True)
    
    target: Path = EXPORT_FOLDER / image_file
    image.save(target, compress_level=9, optimize=True, quality=100)
    
    return target


def check_image(image: Image, image_file: Path) -> Path:
    size: tuple[int, int] = image.size
    pixel_count: int = size[0] * size[1]
    
    if pixel_count > MAX_PIXELS:
        scale: float = sqrt(MAX_PIXELS / pixel_count)
        LOGGER.info(f"{image_file} will be resized to {scale * 100:.2f}%")
        
        image = image.resize((floor(size[0] * scale), floor(size[1] * scale)))
    
    return export_image(image, image_file)


def main() -> None:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("files", nargs="+", help="Which files to resize", type=Path)
    
    args: Namespace = parser.parse_args()
    
    files: list[Path] = args.files
    
    all_exist: bool = True
    for file in files:
        if not file.exists():
            all_exist = False
            LOGGER.error(f"{file} does not exist")
    
    if not all_exist:
        exit(1)
    
    for file in files:
        with Img.open(file) as image:
            LOGGER.verbose_log(f"processing {image}...")
            check_image(image, file)


if __name__ == '__main__':
    main()
