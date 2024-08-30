import sys
from functools import partial
from multiprocessing import Pool, cpu_count
from pathlib import Path
from random import shuffle

import tqdm
from imagehash import ImageHash
from PIL import Image
from pyheif_pillow_opener import register_heif_opener

from .raw import register_raw_opener

register_heif_opener()
register_raw_opener()

ignore = [".mp4", ".mov"]


def hash_image(func, item):
    try:
        img = Image.open(bytes(item))
        img.save("/tmp/t.jpg")
        ihash = func(img)
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
    for ihash, path in image_iter:
        images[str(ihash)].append(str(path))


def hash_list(image_list, func):
    shuffle(image_list)
    with Pool(cpu_count() + 1) as pool:
        hash_func = partial(hash_image, func)
        with tqdm.tqdm(total=len(image_list)) as pbar:
            iter = pool.imap_unordered(hash_func, image_list)
            # iter = map(hash_func, image_list)
            for item in iter:
                ihash, path = item
                pbar.update()
                name = str(path.name)
                space = " " * (30 - len(name))
                pbar.set_description(f"{name}{space}")
                path = path.absolute().resolve()
                if isinstance(ihash, ImageHash):
                    yield item
                else:
                    print(f"{type(item[0]).__name__} could not read image: {path}")
