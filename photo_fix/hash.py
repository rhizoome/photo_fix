import sys
from functools import partial
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from pyheif_pillow_opener import register_heif_opener

register_heif_opener()

ignore = [".mp4", ".mov"]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def hash_image(func, item):
    try:
        img = Image.open(bytes(item))
        hash = func(img)
        return (hash, item)
    except UnidentifiedImageError:
        return (UnidentifiedImageError, item)
    except OSError:
        return (OSError, item)


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
    image_list = hash_list(image_list, func)
    for hash, item in image_list:
        if hash is UnidentifiedImageError:
            eprint(f"Unknown image format {item.absolute()}")
        elif hash is OSError:
            eprint(f"Broken image format {item.absolute()}")
        images[hash].append(item)


def hash_list(image_list, func):
    with Pool() as pool:
        hash_func = partial(hash_image, func)
        return pool.map(hash_func, image_list)
