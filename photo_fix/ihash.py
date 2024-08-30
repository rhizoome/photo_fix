import sys
import traceback
from functools import partial
from multiprocessing import Pool, cpu_count
from pathlib import Path

import tqdm
from imagehash import ImageHash
from PIL import Image
from pyheif_pillow_opener import register_heif_opener

from .raw import register_raw_opener

register_heif_opener()
register_raw_opener()

ignore = [".mp4", ".mov"]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def hash_image(func, item):
    try:
        img = Image.open(bytes(item))
        img.save("/tmp/t.jpg")
        # ihash = func(img)
        ihash = None
        return (ihash, item)
    except Exception as e:
        return (e, item)


def find(dir: Path, images):
    for item in dir.iterdir():
        if item.is_dir():
            find(item, images)
        elif not item.is_symlink():
            if not item.suffix.lower() in ignore:
                images.append(item)


def hash_dir(dir: Path, images, func):
    image_list = []
    find(dir, image_list)
    image_iter = hash_list(image_list, func)
    for ihash, item in image_iter:
        if isinstance(ihash, ImageHash):
            images[str(ihash)].append(str(item))
        else:
            path = item.absolute().resolve()
            print(f"{type(ihash).__name__} could not read image: {path}")


def hash_list(image_list, func):
    with Pool(cpu_count() + 1) as pool:
        hash_func = partial(hash_image, func)
        with tqdm.tqdm(total=len(image_list)) as pbar:
            iter = pool.imap_unordered(hash_func, image_list)
            # iter = map(hash_func, image_list)
            for item in iter:
                pbar.update()
                yield item
