import bz2
import json
import os
import pickle
from collections import defaultdict
from pathlib import Path

import click
import imagehash

from .hash import hash_dir


def compressed_pickle(file_, data):
    if not file_.suffix == ".pbz2":
        raise ValueError("file must have the .pbz2 extension")
    with bz2.BZ2File(str(file_), "wb") as f:
        pickle.dump(data, f)


def decompress_pickle(file_):
    if not file_.suffix == ".pbz2":
        raise ValueError("file must have the .pbz2 extension")
    with bz2.BZ2File(file_, "rb") as f:
        return pickle.load(f)


def dump(directory, images):
    print(json.dumps([str(Path(directory, image).resolve()) for image in images]))


def check_hashes(reference, compare, func):
    reference = Path(reference)
    compare = Path(compare)
    _, reference = decompress_pickle(reference)
    directory, compare = decompress_pickle(compare)
    for hash, images in compare.items():
        if func(hash, reference):
            dump(directory, images)


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
    directory = Path(directory).absolute().resolve()
    output = Path(output).absolute().resolve()
    os.chdir(directory)
    images = defaultdict(list)
    hash_dir(Path("."), images, imagehash.dhash)
    compressed_pickle(output, (directory, images))


@run.command()
@click.argument(
    "input",
    type=click.Path(
        exists=True,
        readable=True,
        dir_okay=False,
        file_okay=True,
    ),
)
def duplicates(input):
    input = Path(input)
    directory, input = decompress_pickle(input)
    for images in input.values():
        if len(images) > 1:
            dump(directory, images)


@run.command()
@click.argument(
    "reference",
    type=click.Path(exists=True, readable=True, dir_okay=False, file_okay=True),
)
@click.argument(
    "compare",
    type=click.Path(exists=True, readable=True, dir_okay=False, file_okay=True),
)
def not_in_ref(reference, compare):
    check_hashes(reference, compare, lambda hash, reference: hash not in reference)


@run.command()
@click.argument(
    "reference",
    type=click.Path(exists=True, readable=True, dir_okay=False, file_okay=True),
)
@click.argument(
    "compare",
    type=click.Path(exists=True, readable=True, dir_okay=False, file_okay=True),
)
def in_ref(reference, compare):
    check_hashes(reference, compare, lambda hash, reference: hash in reference)
