import bz2
import json
import os
from collections import defaultdict
from pathlib import Path

import click
import imagehash

from .ihash import hash_dir


def check_ext(file_):
    if not str(file_).endswith(".json.bz2"):
        raise ValueError("file must have the .json.bz2 extension")


def compressed_json(file_, data):
    check_ext(file_)
    with bz2.open(str(file_), "wt") as f:
        json.dump(data, f)


def decompress_json(file_):
    with bz2.open(file_, "rt") as f:
        return json.load(f)


def dump(directory, images):
    check_ext(file_)
    print(json.dumps([str(Path(directory, image).resolve()) for image in images]))


def check_hashes(reference, compare, func):
    reference = Path(reference)
    compare = Path(compare)
    _, reference = decompress_json(reference)
    directory, compare = decompress_json(compare)
    for ihash, images in compare.items():
        if func(ihash, reference):
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
    check_ext(output)
    os.chdir(directory)
    images = defaultdict(list)
    hash_dir(Path("."), images, imagehash.dhash)
    compressed_json(output, (str(directory), images))


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
    directory, input = decompress_json(input)
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
    check_hashes(reference, compare, lambda ihash, reference: ihash not in reference)


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
    check_hashes(reference, compare, lambda ihash, reference: ihash in reference)
