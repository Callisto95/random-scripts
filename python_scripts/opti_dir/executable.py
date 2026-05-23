from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run
from typing import Callable

from python_scripts.logger import Logger
from python_scripts.opti_dir.stuff import EnvironmentArgument, FileFilter, OptimizationFailed, replace_file_type

__all__ = ["Executable", "Executables"]


LOGGER: Logger = Logger("opti-dir")

# STDOUT_TO_DEVNULL: dict[str, int] = { "stdout": DEVNULL, "stderr": DEVNULL }
CAPTURE_OUTPUT: dict[str, int] = { "capture_output": True, "text": True }


def exec_oxipng(image: Path) -> tuple[CompletedProcess, Path]:
	return run(
		[
			"oxipng",
			f"--opt={EnvironmentArgument.OXI_OPT_LEVEL}",
			"--preserve",
			"--filters",
			"0-9", "--fix",
			"--threads=1",
			image
		],
		**CAPTURE_OUTPUT
	), image


def exec_jpegoptim(image: Path) -> tuple[CompletedProcess, Path]:
	return run(["jpegoptim", "--preserve", image], **CAPTURE_OUTPUT), image


def exec_cjxl(image: Path) -> tuple[CompletedProcess, Path]:
	target: Path = replace_file_type(image, "jxl")
	
	return (
		run(["cjxl", "-d", EnvironmentArgument.JXL_DISTANCE, "-e", "7", image, target], **CAPTURE_OUTPUT),
		target
	)


def exec_jpeg2png(image: Path) -> tuple[CompletedProcess, Path]:
	target: Path = replace_file_type(image, "png")
	
	from python_scripts.opti_dir.feature import InternalFeatures
	if InternalFeatures.USE_16_BIT.enabled:
		return run(
			["jpeg2png", "--threads", "1", "--16-bits-png", "--iterations", "150", image, "--output", target],
			**CAPTURE_OUTPUT
		), target
	else:
		return run(["jpeg2png", "--threads", "1", image, "--output", target], **CAPTURE_OUTPUT), target


def exec_dwebp(image: Path) -> tuple[CompletedProcess, Path]:
	target: Path = replace_file_type(image, "png")
	
	return run(["dwebp", image, "-o", target], **CAPTURE_OUTPUT), target


@dataclass
class Executable:
	binary: str
	filter: Callable[[Path], bool]
	execute: Callable[[Path], tuple[CompletedProcess, Path]]
	available: bool = field(init=False)
	
	def __post_init__(self):
		self.available = self.executable_is_available(self.binary)
	
	@staticmethod
	def executable_is_available(command: str) -> bool:
		path: str | None = which(command)
		if path is None:
			LOGGER.verbose_log(f"'{command}' is not installed")
			return False
		return True
	
	def run(self, image: Path, previous_result: CompletedProcess | None = None) -> tuple[CompletedProcess | None, Path]:
		"""Run the associated program on the given image
		:param image: The image to optimize (either visual clarity or size)
		:param previous_result: Convenience: If either the filter or the program is not available, return this.
		:return: The process result or None if the file doesn't match or the program isn't available, and the new
		image path.
		"""
		if self.available and self.filter(image):
			result, image = self.execute(image)
			
			if result is not None and result.returncode != 0:
				raise OptimizationFailed(result, image)
			
			if result is None:
				result = previous_result
			return result, image
		
		return previous_result, image


class Executables(Executable, Enum):
	OXIPNG = "oxipng", FileFilter.png, exec_oxipng
	JPEGOPTIM = "jpegoptim", FileFilter.jpeg, exec_jpegoptim
	CJXL = "cjxl", FileFilter.any, exec_cjxl
	JPEG2PNG = "jpeg2png", FileFilter.jpeg, exec_jpeg2png
	DWEBP = "dwebp", FileFilter.webp, exec_dwebp
