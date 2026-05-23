#!/usr/bin/python
import os
import sys
from pathlib import Path

from mutagen import FileType, File
from mutagen.id3 import TIT2

errors: list[tuple[str, Exception]] = []

for file in os.listdir():
    try:
        tag: FileType = File(file)
        
        if tag is None:
            print(f"unsupported format: {file}")
            continue
        
        if "TIT2" in tag.tags:
            print(f"{file} has title already")
            continue
        
        title: str = Path(file).stem.replace("-", " ")
        
        tag.tags.add(TIT2(text=title))
        tag.save()
    except Exception as exc:
        errors.append((file, exc))

print()
for error in errors:
    print(f"an error occurred with file {error[0]}: {error[1]}", file=sys.stderr)

exit(len(errors))
