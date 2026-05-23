import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import DEVNULL, run
from tempfile import NamedTemporaryFile

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from python_scripts.quickbac.crop import Cropper
from python_scripts.quickbac.data import ImageProcessorFactory
from python_scripts.quickbac.fill import Filler
from python_scripts.quickbac.ui import ExternalResult, QuickBackUI

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


def run_gimp(image: QImage, path: Path) -> ExternalResult:
    with NamedTemporaryFile("w", suffix=path.suffix) as file:
        image.save(file.name, format="png")
        
        run(["gimp", file.name], stdout=DEVNULL, stderr=DEVNULL)
        
        result: QImage = QImage(file.name)
        
        return ExternalResult(path, result)


app: QApplication = QApplication([sys.argv[0]] + args.qt_args.split(","))

decider: ImageProcessorFactory = ImageProcessorFactory()

ui: QuickBackUI = QuickBackUI(
    decider, args.output_directory.absolute(), {
        "Gimp": run_gimp,
    },
)

decider.register(True, False, Filler(ui.pc_ratio, True))
decider.register(True, True, Cropper(ui.pc_ratio))
decider.register(False, False, Filler(ui.phone_ratio, False))
decider.register(False, True, Cropper(ui.phone_ratio))

ui.show()
sys.exit(app.exec())
