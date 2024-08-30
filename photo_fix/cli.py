import bz2
import pickle
from collections import defaultdict
from pathlib import Path

import click
import imagehash

from .hash import hash_dir


def compressed_pickle(file_, data):
    with bz2.BZ2File(str(file_), "wb") as f:
        pickle.dump(data, f)


def decompress_pickle(file_):
    with bz2.BZ2File(file_, "rb") as f:
        return pickle.load(f)


@click.group()
def run():
    pass


@run.command()
@click.argument(
    "directory",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        readable=True,
    ),
)
@click.argument(
    "output", type=click.Path(writable=True, dir_okay=False, file_okay=True)
)
def ihash(directory, output):
    directory = Path(directory)
    images = defaultdict(list)
    hash_dir(directory, images, imagehash.dhash)
    compressed_pickle(output, images)


@run.command()
@click.argument("input", type=click.Path(readable=True, dir_okay=False, file_okay=True))
def duplicates(input):
    images = decompress_pickle(input)
    for images in images.values():
        if len(images) > 1:
            print(images)


@run.command()
@click.argument("reference")
@click.argument("clean")
def compare(reference, clean):
    pass
