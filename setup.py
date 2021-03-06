#!/usr/bin/python3

# Copyright (C) 2018-2019, Benjamin Drung <benjamin.drung@cloud.ionos.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Setup for ionit"""

import subprocess

from setuptools import setup


def systemd_unit_path():
    """Determine path for systemd units"""
    try:
        command = ["pkg-config", "--variable=systemdsystemunitdir", "systemd"]
        path = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return path.decode().replace("\n", "")
    except (subprocess.CalledProcessError, OSError):
        return "/lib/systemd/system"


if __name__ == "__main__":
    setup(
        name="ionit",
        version="0.3.6",
        description="Render configuration files from Jinja templates",
        long_description=(
            "ionit is a simple and small configuration templating tool. It collects a context and "
            "renders Jinja templates in a given directory. The context can be either static JSON "
            "or YAML files or dynamic Python files. Python files can also define functions passed "
            "through to the rendering."
        ),
        author="Benjamin Drung",
        author_email="benjamin.drung@cloud.ionos.com",
        url="https://github.com/bdrung/ionit",
        license="ISC",
        install_requires=["jinja2"],
        scripts=["ionit"],
        py_modules=["ionit_plugin"],
        data_files=[(systemd_unit_path(), ["ionit.service"])],
    )
