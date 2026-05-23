from os import listdir, utime
from os.path import getmtime, isdir

from PIL import Image

icc_profile: str = "icc_profile"

for img in listdir():
    if isdir(img):
        continue
    
    mtime: float = getmtime(img)
    
    with Image.open(img) as image:
        if icc_profile in image.info:
            image.info = {icc_profile: image.info[icc_profile]}
        else:
            image.info = {}
        
        image.save(img)
    
    utime(img, (mtime, mtime))
