# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["photo_fix"]

package_data = {"": ["*"]}

install_requires = [
    "ImageHash",
    "click",
    "pyheif-pillow-opener",
    "python-magic",
    "rawpy",
    "tqdm",
]

entry_points = {"console_scripts": ["photo-fix = photo_fix.cli:run"]}

setup_kwargs = {
    "name": "photo-fix",
    "version": "0.1.0",
    "description": "",
    "long_description": None,
    "author": "Stream Punk",
    "author_email": "glad.car1474@fastmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": None,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.9,<4.0",
}


setup(**setup_kwargs)
