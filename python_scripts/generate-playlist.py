#!/usr/bin/env python

import os
from pathlib import Path

from tinytag import TinyTag

files: list[tuple[Path, TinyTag]] = [(Path(file), TinyTag.get(file)) for file in os.listdir() if TinyTag.is_supported(file)]

files.sort(key=lambda tup: tup[0])
files.sort(key=lambda tup: tup[1].track if tup[1].track else 0)

for file in files:
    print(file[0].absolute())
