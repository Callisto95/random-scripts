import os
from asyncio import Future
from enum import StrEnum
from os.path import exists, getsize
from pathlib import Path
from subprocess import CompletedProcess
from typing import Callable, TypeAlias

from python_scripts.logger import Logger


LOGGER: Logger = Logger("opti-dir")


def filter_tasks(tasks: list[tuple[Path, Future[tuple[CompletedProcess, Path]]]]) -> int:
	return len(list(filter(lambda task: task[1].done(), tasks)))


def get_size_of_files(images: list[Path]) -> int:
	return sum(getsize(image) for image in images if exists(image))


def replace_file_type(file: Path, target: str) -> Path:
	return file.with_suffix(f".{target}")


class FileFilter:
	type: TypeAlias = Callable[[Path], bool]
	
	@staticmethod
	def jpeg(path: Path) -> bool:
		return path.suffix in (".jpg", ".jpeg")
	
	# using '==' for safety
	# -> prevent weird 'character is in string' testing behaviour
	@staticmethod
	def jxl(path: Path) -> bool:
		return path.suffix == ".jxl"
	
	@staticmethod
	def png(path: Path) -> bool:
		return path.suffix == ".png"
	
	@staticmethod
	def webp(path: Path) -> bool:
		return path.suffix == ".webp"
	
	@staticmethod
	def any(path: Path) -> bool:
		# .jxl files are considered optimized
		return path.suffix in (".jpg", ".jpeg", ".png", ".webp")


class EnvironmentArgument(StrEnum):
	JXL_DISTANCE = os.environ.setdefault("JXL_DISTANCE", "1")
	OXI_OPT_LEVEL = os.environ.setdefault("OXI_OPT_LEVEL", "2")
	
	@classmethod
	def list_for_user(cls) -> None:
		LOGGER.log("Environment:")
		for member in cls:
			# member is an enum member and has a 'name' attribute
			LOGGER.log(f"{member.name}\t{member}")


class OptimizationFailed(Exception):
	def __init__(self, failed_task: CompletedProcess, image: Path):
		self.failed_task = failed_task
		self.image = image
	
	def __str__(self) -> str:
		return f"The optimization of '{self.image}' failed with {self.failed_task.returncode} ({self.failed_task.stdout})"
