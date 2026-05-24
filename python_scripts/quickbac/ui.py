#!/usr/bin/python
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from typing import Any, Callable

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QColorSpace,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QImage,
    QKeyEvent,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import QFileDialog, QMainWindow

from python_scripts.logger import Logger
from python_scripts.quickbac.data import ImageModifier, ImageProcessorFactory, Offsets, RatioSelector
from python_scripts.quickbac.ui_raw import Ui_MainWindow

LOGGER: Logger = Logger("QuickBacUI")
ZOOM_NORMAL: int = 500


@dataclass(frozen=True)
class ExternalResult:
    new_path: Path
    image: QImage


class ExternalProcessThread(QThread):
    resultReady = Signal(ExternalResult)
    
    def __init__(self, function: Callable[[QImage, Path], ExternalResult], args: list[Any]):
        super().__init__()
        self.function: Callable[[QImage, Path], ExternalResult] = function
        self.args: list[Any] = args
    
    def run(self, /):
        try:
            result: ExternalResult = self.function(*self.args)
            self.resultReady.emit(result)
        except Exception as exc:
            LOGGER.error(exc)


class QuickBackUI(QMainWindow):
    def __init__(
        self,
        decider: ImageProcessorFactory,
        output_directory: Path | None,
        commands: dict[str, Callable[[QImage, Path], ExternalResult]],
    ):
        super().__init__()
        
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.connect_signals()
        
        self.commands: dict[str, Callable[[QImage, Path], ExternalResult]] = commands
        self.output_directory: Path | None = None if output_directory is None else output_directory.absolute()
        
        # do not GC the thread. It will crash the app
        self.external_process: ExternalProcessThread | None = None
        
        self.update_timer: QTimer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(1)
        self.update_timer.timeout.connect(self._do_update)
        
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.pending_future: Future[QImage] | None = None
        
        self.pc_ratio: RatioSelector = RatioSelector([(3840, 2160)])
        self.phone_ratio: RatioSelector = RatioSelector([(1080, 2400), (1116, 2484)])
        
        self.decider: ImageProcessorFactory = decider
        
        self.current_image_path: Path | None = None
        self.current_image: QImage | None = None
        self.finished_image: QImage | None = None
        
        self.ui.commands.addItems(list(commands.keys()))
        
        self.reset()
        self.rotate_horizontal_ratio(skip_advance=True)
        self.rotate_vertical_ratio(skip_advance=True)
    
    def connect_signals(self) -> None:
        self.ui.horizontal.toggled.connect(self.update_current_image)
        self.ui.fill.toggled.connect(self.update_current_image)
        self.ui.crop.toggled.connect(self.update_current_image)
        self.ui.offset_primary.valueChanged.connect(self.update_current_image)
        self.ui.offset_secondary.valueChanged.connect(self.update_current_image)
        self.ui.zoom.valueChanged.connect(self.update_current_image)
        self.ui.vertical_33_percent.checkStateChanged.connect(self.update_current_image)
        self.ui.vertical_50_percent.checkStateChanged.connect(self.update_current_image)
        self.ui.vertical_66_percent.checkStateChanged.connect(self.update_current_image)
        self.ui.horizontal_33_percent.checkStateChanged.connect(self.update_current_image)
        self.ui.horizontal_50_percent.checkStateChanged.connect(self.update_current_image)
        self.ui.horizontal_66_percent.checkStateChanged.connect(self.update_current_image)
        self.ui.center.clicked.connect(self.reset_offset)
        self.ui.export.clicked.connect(self.export)
        self.ui.commands.currentIndexChanged.connect(self.run_program_index)
        
        self.ui.horizontal.mouseDoubleClickEvent = self.rotate_horizontal_ratio
        self.ui.vertical.mouseDoubleClickEvent = self.rotate_vertical_ratio
    
    def run_program_index(self) -> None:
        if self.ui.commands.currentIndex() == -1 or self.current_image is None:
            self.ui.commands.setCurrentIndex(-1)
            return
        
        self.setEnabled(False)
        
        self.external_process = ExternalProcessThread(
            self.commands[self.ui.commands.currentText()],
            [self.current_image, self.current_image_path],
        )
        self.external_process.resultReady.connect(self.finish_run_program)
        self.external_process.start()
    
    def finish_run_program(self, result: ExternalResult) -> None:
        if result is None:
            LOGGER.error("Invalid result from external program!")
            return
        
        LOGGER.info("updating from subprocess...")
        
        self.current_image_path = result.new_path
        result.image.setColorSpace(self.current_image.colorSpace())
        self.current_image = result.image
        
        self.update_current_image()
        
        self.setEnabled(True)
        
        self.ui.commands.setCurrentIndex(-1)
        self.external_process = None
    
    def rotate_horizontal_ratio(self, *_, skip_advance: bool = False) -> None:
        ratio: tuple[int, int] = self.pc_ratio.current() if skip_advance else self.pc_ratio.advance()
        
        self.ui.horizontal.setText(
            f"Horizontal {ratio[0]}x{ratio[1]} [{self.pc_ratio.index + 1}/{len(self.pc_ratio.ratios)}]",
        )
        self.update_current_image()
    
    def rotate_vertical_ratio(self, *_, skip_advance: bool = False) -> None:
        ratio: tuple[int, int] = self.phone_ratio.current() if skip_advance else self.phone_ratio.advance()
        
        self.ui.vertical.setText(
            f"Vertical {ratio[0]}x{ratio[1]} [{self.phone_ratio.index + 1}/{len(self.phone_ratio.ratios)}]",
        )
        self.update_current_image()
    
    def get_offsets(self) -> Offsets:
        return Offsets(
            self.ui.offset_primary.value() / (self.ui.offset_primary.maximum() / 2),
            self.ui.offset_secondary.value() / (self.ui.offset_secondary.maximum() / 2),
            self.ui.zoom.value() / ZOOM_NORMAL,
        )
    
    def export(self) -> None:
        if not self.current_image:
            return
        
        if self.output_directory is not None:
            path: Path = self.output_directory / self.current_image_path.name
        else:
            path: Path = self.current_image_path
        
        url, _ = QFileDialog.getSaveFileUrl(self, caption="Export as", dir=QUrl.fromLocalFile(path))
        
        if url.path() != "":
            path: Path = Path(url.toLocalFile())
            
            if not path.suffix:
                LOGGER.warn("no type in filename - defaulting to PNG.")
                path = path.with_suffix(".png")
            
            LOGGER.info("exporting image as", path)
            # quality 0 compresses the image, causing the UI to freeze
            # offload to another thread to keep the UI running
            copied_image: QImage = self.finished_image.copy()
            Thread(target=lambda: copied_image.save(str(path), quality=0)).start()
    
    def _do_update(self) -> None:
        if not self.current_image:
            return
        
        # cancel any in-flight work
        if self.pending_future is not None and not self.pending_future.done():
            self.pending_future.cancel()
        
        modifier: ImageModifier = self.decider.get(self.ui.horizontal.isChecked(), self.ui.crop.isChecked())
        offsets: Offsets = self.get_offsets()
        image: QImage = self.current_image.copy()
        
        # snapshot everything the thread needs, then submit
        self.pending_future: Future[QImage] = self.executor.submit(
            modifier.modify,
            image,
            offsets,
            self.pc_ratio.current_ratio() if self.ui.horizontal.isChecked() else self.phone_ratio.current_ratio(),
        )
        self.pending_future.add_done_callback(self._on_update_done)
    
    def _on_update_done(self, future) -> None:
        if future.cancelled():
            return
        
        self.finished_image = future.result()
        
        scaled_image: QImage = self.finished_image.scaled(
            self.ui.image.size(),
            aspectMode=Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.draw_guides(scaled_image)
        # this is far better than no colour space conversion, but very much not perfect!
        converted_image: QImage = scaled_image.convertedToColorSpace(QColorSpace.NamedColorSpace.SRgb)
        
        self.ui.image.setPixmap(QPixmap.fromImage(converted_image))
        
        self.setWindowTitle(
            f"{self.current_image_path.name} - {self.finished_image.width()}x{self.finished_image.height()} - QuickBac",
        )
    
    def draw_guides(self, image: QImage) -> None:
        painter: QPainter = QPainter(image)
        
        painter.setPen(QColor(255, 0, 0))
        
        def draw_vertical_line(x_position: float) -> None:
            x: int = round(x_position)
            painter.drawLine(x, 0, x, image.height())
        
        if self.ui.vertical_33_percent.isChecked():
            draw_vertical_line(image.width() / 3)
        if self.ui.vertical_50_percent.isChecked():
            draw_vertical_line(image.width() / 2)
        if self.ui.vertical_66_percent.isChecked():
            draw_vertical_line(image.width() / 3 * 2)
        
        def draw_horizontal_line(y_position: float) -> None:
            y: int = round(y_position)
            painter.drawLine(0, y, image.width(), y)
        
        if self.ui.horizontal_33_percent.isChecked():
            draw_horizontal_line(image.height() / 3)
        if self.ui.horizontal_50_percent.isChecked():
            draw_horizontal_line(image.height() / 2)
        if self.ui.horizontal_66_percent.isChecked():
            draw_horizontal_line(image.height() / 3 * 2)
        
        painter.end()
    
    def update_current_image(self) -> None:
        if not self.current_image:
            return
        
        if self.ui.crop.isChecked():
            self.ui.zoom.setMaximum(ZOOM_NORMAL)
        else:
            self.ui.zoom.setMaximum(ZOOM_NORMAL * 2)
        self.ui.offset_secondary.setEnabled(self.ui.zoom.value() != ZOOM_NORMAL)
        
        self.update_timer.start()
    
    def reset_offset(self) -> None:
        self.ui.offset_primary.setValue(round(self.ui.offset_primary.maximum() / 2))
        self.ui.offset_secondary.setValue(round(self.ui.offset_secondary.maximum() / 2))
        self.ui.zoom.setValue(ZOOM_NORMAL)
        self.ui.offset_secondary.setEnabled(False)
    
    def reset(self) -> None:
        self.current_image = None
        self.finished_image = None
        self.current_image_path = None
        self.ui.image.setPixmap(QPixmap())
        
        self.reset_offset()
        
        self.ui.vertical_33_percent.setChecked(False)
        self.ui.vertical_50_percent.setChecked(False)
        self.ui.vertical_66_percent.setChecked(False)
        self.ui.horizontal_33_percent.setChecked(False)
        self.ui.horizontal_50_percent.setChecked(False)
        self.ui.horizontal_66_percent.setChecked(False)
    
    def resizeEvent(self, event, /) -> None:
        self.update_current_image()
    
    def dropEvent(self, event: QDropEvent, /) -> None:
        self.reset()
        
        file_path: str = event.mimeData().urls()[0].toLocalFile()
        self.current_image_path: Path = Path(file_path)
        self.current_image = QImage(self.current_image_path)
        
        LOGGER.info(f"new image: {file_path}")
        
        self.update_current_image()
    
    @staticmethod
    def _accept_event(event: QDragEnterEvent | QDragMoveEvent) -> None:
        if event.mimeData().hasUrls and len(event.mimeData().urls()) == 1:
            event.accept()
        else:
            event.ignore()
    
    def dragEnterEvent(self, event: QDragEnterEvent, /) -> None:
        self._accept_event(event)
    
    def dragMoveEvent(self, event: QDragMoveEvent, /) -> None:
        self._accept_event(event)
    
    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            self.close()
