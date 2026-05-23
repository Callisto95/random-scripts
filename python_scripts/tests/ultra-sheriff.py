from asyncio import Future
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from os import cpu_count
from pathlib import Path
from time import sleep
from typing import Any

import requests
from progressbar import ProgressBar
from requests import Response

REQUEST_URI: str = "http://ultrasheriff.com/services/terminal/command.php?value={query}"
WORDS_FILE: Path = Path("/run/media/luca_s/Data-2TB/workspace/english-words/words.txt")


@dataclass
class WebsiteResponse:
	word: str
	message: str
	color: str
	animate: bool
	speed: int
	media: Any
	done_message: str


print("loading words...")
with WORDS_FILE.open("r") as words_file:
	words: list[str] = [word[:-1] for word in words_file.readlines()]
print("done")

ALL_WORDS: int = len(words)
DONE_WORDS: int = 0


def evaluate_response(response: Future[WebsiteResponse]) -> None:
	global DONE_WORDS
	DONE_WORDS += 1
	
	result: WebsiteResponse = response.result()
	
	if result.media is not None:
		print(f"\r\u001B[0J'{result.word}': FOUND MEDIA: '{result.media}'")
	
	if result.message != "Negative.":
		print(f"\r\u001B[0J'{result.word}': FOUND SPECIAL MESSAGE: '{result.message}'")
	
	# 'NULL' is there every time message is not 'Negative.', otherwise empty string
	if result.done_message != "" and result.done_message != "NULL":
		print(f"\r\u001B[0J'{result.word}': FOUND SPECIAL DONE MESSAGE: '{result.done_message}'")


EXECUTOR: ThreadPoolExecutor = ThreadPoolExecutor(cpu_count())
# EXECUTOR: ThreadPoolExecutor = ThreadPoolExecutor(256)


def request_word(word: str) -> WebsiteResponse:
	response: Response = requests.get(REQUEST_URI.format(query=word))
	return WebsiteResponse(word, **response.json())


print("queuing requests...")
tasks: list[Future[WebsiteResponse]]
for word in words:
	task: Future[WebsiteResponse] = EXECUTOR.submit(request_word, word)
	task.add_done_callback(evaluate_response)
print("done")

try:
	progress_bar: ProgressBar = ProgressBar(max_value=ALL_WORDS)
	progress_bar.update(0)
	while DONE_WORDS < ALL_WORDS:
		progress_bar.update(DONE_WORDS)
		sleep(1)
except KeyboardInterrupt:
	EXECUTOR.shutdown(cancel_futures=True)
