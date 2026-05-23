from __future__ import annotations

import shutil
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from os import listdir, utime
from os.path import exists, getmtime
from pathlib import Path
from subprocess import CompletedProcess
from time import sleep

from colorama import Fore, Style
from progress.bar import Bar, IncrementalBar
from progress.spinner import PixelSpinner, Spinner

from python_scripts import pretty_print_bytes
from python_scripts.logger import Logger
from python_scripts.opti_dir.executable import Executable, Executables
from python_scripts.opti_dir.feature import Features
from python_scripts.opti_dir.stuff import (
	FileFilter,
	filter_tasks,
	get_size_of_files,
	OptimizationFailed,
	replace_file_type
)

__all__ = ["optimize_directory", "OptimizationResult"]


LOGGER: Logger = Logger("opti-dir")


type OptimizationResult = tuple[Path, Future[CompletedProcess, Path]]

EXECUTOR: ThreadPoolExecutor | None = None
MINIMUM_PROGRESS_BAR_WIDTH: int = 30

DELETED_IMAGE_FOLDER: Path = Path("./deleted-images/").expanduser().resolve().absolute()


def delete_image(image: Path) -> None:
	if not exists(image):
		return
	
	if not DELETED_IMAGE_FOLDER.exists() or not DELETED_IMAGE_FOLDER.is_dir():
		DELETED_IMAGE_FOLDER.mkdir()
	
	image.replace(DELETED_IMAGE_FOLDER / image.name)


class FileHeaders(bytes, Enum):
	# https://en.wikipedia.org/wiki/List_of_file_signatures
	JPEG = b"\xFF\xD8\xFF"
	PNG = b"\x89\x50\x4E\x47"
	WEBP_START = b"\x52\x49\x46\x46"
	WEBP_END = b"\x57\x45\x42\x50"
	
	@classmethod
	def header_length_to_read(cls) -> int:
		# TODO: can this be automated?
		return 3 * len(cls.WEBP_START)
	
	@classmethod
	def determine_actual_image(cls, image: Path) -> Path:
		with image.open("rb") as file:
			header: bytes = file.read(FileHeaders.header_length_to_read())
		
		if header.startswith(cls.JPEG):
			image = replace_file_type(image, "jpg")
		elif header.startswith(cls.PNG):
			image = replace_file_type(image, "png")
		elif header[0:4] == cls.WEBP_START and header[8:12] == cls.WEBP_END:
			image = replace_file_type(image, "webp")
		
		return image


def fix_image(image: Path) -> Path:
	actual_image: Path = FileHeaders.determine_actual_image(image)
	
	if actual_image != image:
		LOGGER.verbose_log(f"\r\u001B[0JFound bad file extension: {image} -> {actual_image}")
		image.rename(actual_image)
	# shutil.move(original, image)
	
	return actual_image


def optimize_image(image: Path) -> tuple[CompletedProcess, Path]:
	try:
		if Features.FIX_IMAGES.enabled:
			# this version *is* the real image
			image = fix_image(image)
		
		intermediary_images: list[Path] = []
		result: CompletedProcess | None = None
		
		if Features.WEBP_DECODE.should_run_on(image):
			intermediary_images.append(Path(image))
			result, image = Executables.DWEBP.run(image, result)
		
		if Features.JPEG_BETTER_DECODE.should_run_on(image):
			# preserve modification time
			modification_time: float = getmtime(image)
			
			intermediary_images.append(Path(image))
			result, image = Executables.JPEG2PNG.run(image, result)
			
			# (access time, modification time) - just set both to modification_time
			utime(image, (modification_time, modification_time))
		
		# if the file doesn't match, it's not run
		result, image = Executables.OXIPNG.run(image, result)
		result, image = Executables.JPEGOPTIM.run(image, result)
		
		if Features.JXL_ENCODE.enabled:
			intermediary_images.append(Path(image))
			result, image = Executables.CJXL.run(image, result)
		
		if Features.DELETE_ORIGINAL.enabled:
			while len(intermediary_images) != 0:
				intermediary: Path = intermediary_images.pop()
				
				if intermediary == image:
					continue
				
				delete_image(intermediary)
		
		return result, image
	
	# some step has failed and cannot be recovered from
	except OptimizationFailed as exc:
		return exc.failed_task, exc.image


@dataclass
class FilterAndRequirements:
	filter: FileFilter.type
	requirements: list[Executable]
	all_requirements_needed: bool = True


class FileType(FilterAndRequirements, Enum):
	JPEG = FileFilter.jpeg, [Executables.JPEGOPTIM, Executables.JPEG2PNG], False
	PNG = FileFilter.png, [Executables.OXIPNG]
	WEBP = FileFilter.webp, [Executables.DWEBP]


def optimize_type(
	type_: FileType,
	files: list[Path]
) -> tuple[list[OptimizationResult], int]:
	availability: list[bool] = [requirement.available for requirement in type_.requirements]
	
	if type_.all_requirements_needed:
		can_run: bool = False not in availability
	else:
		can_run: bool = True in availability
	
	if not can_run:
		LOGGER.info(f"skipping {type_.name} optimization")
		return [], 0
	
	images: list[Path] = [file for file in files if file.is_file() and not file.is_symlink() and type_.filter(file)]
	image_size: int = get_size_of_files(images)
	
	tasks: list[OptimizationResult] = []
	for image in images:
		task: Future[CompletedProcess, Path] = EXECUTOR.submit(optimize_image, image)
		tasks.append((image, task))
	
	if len(tasks) > 0:
		LOGGER.log(f"-> {type_.name}: {len(tasks)}")
		do_progress_bar(tasks)
	else:
		LOGGER.verbose_log(f"{type_.name}: nothing to optimize")
	
	return tasks, image_size


def optimize_directory(directory: Path, threads: int, print_result: bool = True, types: list[FileType] = None) -> None:
	global EXECUTOR
	EXECUTOR = ThreadPoolExecutor(threads)
	
	if types is None:
		types = [f for f in FileType]
	
	files: list[Path] = [Path(path) for path in listdir(directory)]
	files = [(directory / file) for file in files if FileFilter.any(file)]
	
	tasks: list[OptimizationResult] = []
	
	image_size: int = 0
	
	for type_ in types:
		new_tasks, new_image_size = optimize_type(type_, files)
		image_size += new_image_size
		tasks += new_tasks
	
	if len(tasks) == 0:
		LOGGER.info("nothing to optimize")
		return
	
	if print_result:
		print_results(image_size, tasks)


def do_progress_bar(tasks: list[OptimizationResult]) -> None:
	all_tasks: int = len(tasks)
	
	terminal_width: int = shutil.get_terminal_size()[0]
	
	progress_bar_offset_base: int = 10  # 'Progress |' - left side
	progress_bar_offset_numbers: int = 3 + 2 * len(str(all_tasks))  # '| ' and '/' + numbers
	
	progress_bar_width: int = terminal_width - progress_bar_offset_base - progress_bar_offset_numbers
	is_bar: bool = progress_bar_width >= MINIMUM_PROGRESS_BAR_WIDTH
	
	if is_bar:
		bar: Bar = IncrementalBar("Progress", max=all_tasks, width=progress_bar_width, color='cyan')
	else:
		bar: Spinner = PixelSpinner("Processing ")
	
	try:
		done: int = 0
		counter: int = 0
		while done != all_tasks:
			if is_bar:
				done = filter_tasks(tasks)
				bar.goto(done)
				
				if done == all_tasks:
					bar.color = "green"
					bar.update()
					break
				
				sleep(1)
			else:
				counter += 1
				if counter == 10:
					done = filter_tasks(tasks)
					counter = 0
				bar.next()
				sleep(0.1)
		
		bar.finish()
	except KeyboardInterrupt as kbe:
		if is_bar:
			bar.color = "red"
		raise kbe


def print_results(original_size: int, tasks: list[tuple[Path, Future[CompletedProcess, Path]]]) -> None:
	failed_tasks: list[tuple[Path, Future[CompletedProcess, Path]]] = [
		task for task in tasks if task[1].result()[0].returncode != 0
	]
	if len(failed_tasks) > 0:
		with open("/tmp/opti-dir.log", "w") as log_file:
			
			LOGGER.error(f"some tasks ({len(failed_tasks)}) have failed!")
			
			LOGGER.log("failed images:")
			for task in failed_tasks:
				result: CompletedProcess = task[1].result()[0]
				failed_image: Path = task[0]
				
				LOGGER.log(f"\t{failed_image}")
				
				log_file.write(f"file: '{failed_image}', reason:\n")
				log_file.write(result.stdout)
				log_file.write("\n")
			
			LOGGER.info(f"more info can be found in the log file '{log_file.name}'")
		LOGGER.info("Because of the error(s), the resulting size difference calculations are wrong! Use with caution.")
	
	current_size: int = get_size_of_files(
		[task[1].result()[1] for task in tasks if task[1].result()[0].returncode == 0]
	)
	
	size_difference: float = 100 - ((current_size / original_size) * 100)
	is_less: bool = size_difference < 0
	size_difference: float = abs(size_difference)
	LOGGER.log(
		pretty_print_bytes(original_size),
		"->",
		pretty_print_bytes(current_size),
		"(",
		f"{f"{Fore.RED}+" if is_less else Fore.CYAN}{pretty_print_bytes(current_size - original_size)}",
		"|",
		f"{"+" if is_less else "-"}{size_difference:.2f}%{Style.RESET_ALL}",
		")"
	)
