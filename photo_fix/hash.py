from functools import partial
from multiprocessing import Pool
from pathlib import Path

from PIL import Image

ignore = [".mp4", ".mov"]


def hash_image(func, item):
    img = Image.open(bytes(item))
    hash = func(img)
    return (hash, item)


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
        images[hash].append(item)


def hash_list(image_list, func):
    with Pool() as pool:
        hash_func = partial(hash_image, func)
        return pool.map(hash_func, image_list)
