import time

import progressbar
from alive_progress import alive_bar
from alive_progress.styles import showtime
from tqdm import tqdm

RANGE: int = 50
RANGE_OFFSET: int = 1

print(1)
for i in tqdm(range(RANGE)):
	time.sleep(0.1)

print(2)
for i in tqdm(
	range(RANGE),
	desc="Processing files",
	unit="files",
	ncols=75,
	colour='#37B6BD',
):
	time.sleep(0.1)

print(3)
bar = progressbar.ProgressBar(max_value=RANGE)
for i in range(50):
	time.sleep(0.1)
	bar.update(i + RANGE_OFFSET)

print()

print(4)
widgets = [
	'Processing: ', progressbar.Percentage(),
	' ', progressbar.Bar(marker='*', left='[', right=']'),
	' ', progressbar.Counter(), f"/{RANGE}",
	' ', progressbar.Timer(),
	' ', progressbar.ETA()
]
bar = progressbar.ProgressBar(widgets=widgets, max_value=RANGE)
for i in range(RANGE):
	time.sleep(0.1)
	bar.update(i + RANGE_OFFSET)

print()

print(5)
with alive_bar(RANGE) as bar:
	for i in range(RANGE):
		time.sleep(0.1)
		bar()

print(6)
with alive_bar(RANGE, bar='blocks', spinner='arrow', length=50, title='Processing files') as bar:
	for i in range(RANGE):
		time.sleep(0.1)
		bar()

# shows a LOT of bars
# showtime()
