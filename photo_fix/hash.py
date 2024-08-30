from multiprocessing import Pool
from pathlib import Path

import imagehash
from PIL import Image

ignore = [".mp4", ".mov"]


def hash_image(item):
    img = Image.open(bytes(item))
    hash = imagehash.average_hash(img)
    return (hash, item)


def find(dir: Path, images):
    for item in dir.iterdir():
        if item.is_dir():
            find(item, images)
        elif not item.is_symlink():
            if not item.suffix.lower() in ignore:
                images.append(item)


def hash_dir(dir: Path, images):
    image_list = []
    find(dir, image_list)
    with Pool() as pool:
        image_list = pool.map(hash_image, image_list)
    for hash, item in image_list:
        images[hash].append(item)
