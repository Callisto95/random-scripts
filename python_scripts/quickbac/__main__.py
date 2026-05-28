import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import DEVNULL, run
from tempfile import NamedTemporaryFile

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from .crop import Cropper
from .data import ImageProcessorFactory
from .fill import Filler
from .ui import LoadedImage, QuickBackUI

parser: ArgumentParser = ArgumentParser()
parser.add_argument(
    "--output-directory",
    dest="output_directory",
    nargs="?",
    default=None,
    type=Path,
    help="Directory where the export dialog should open in",
)
parser.add_argument(
    "--qt-args",
    type=str,
    default="",
    dest="qt_args",
    help="Comma separated list of arguments to pass to the QApplication",
)
args: Namespace = parser.parse_args()


def run_gimp(loaded_image: LoadedImage) -> LoadedImage:
    with NamedTemporaryFile("w", suffix=loaded_image.path.suffix) as file:
        loaded_image.image.save(file.name, format="png")
        
        run(["gimp", file.name], stdout=DEVNULL, stderr=DEVNULL)
        
        result: QImage = QImage(file.name)
        
        return LoadedImage(loaded_image.path, result)


app: QApplication = QApplication([sys.argv[0]] + args.qt_args.split(","))

decider: ImageProcessorFactory = ImageProcessorFactory()

decider.register(True, False, Filler(True))
decider.register(True, True, Cropper())
decider.register(False, False, Filler(False))
decider.register(False, True, Cropper())

ui: QuickBackUI = QuickBackUI(
    decider, args.output_directory, {
        "Gimp": run_gimp,
    },
)

ui.show()
sys.exit(app.exec())
