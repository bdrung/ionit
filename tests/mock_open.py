# The MIT License (MIT)

# Copyright (c) 2013 Ionuț Arțăriși <ionut@artarisi.eu>
#               2018-2022 Benjamin Drung <bdrung@posteo.de>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Helper function to mock the builtin open() function

Origin: https://github.com/mapleoin/mock_open
"""


import contextlib
import io
import unittest.mock


class NotMocked(Exception):
    """Raised when a file was opened which was not mocked"""

    def __init__(self, filename):
        super().__init__(f"The file {filename} was opened, but not mocked.")
        self.filename = filename


@contextlib.contextmanager
def mock_open(filename, contents=None, exception=None, complain=True):
    """Mock the open() builtin function on a specific filename

    Let execution pass through to open() on files different than
    :filename:. Return a StringIO with :contents: if the file was
    matched. If the :contents: parameter is not given or if it is None,
    a StringIO instance simulating an empty file is returned.

    If :exception: is defined, this Exception will be raised when
    open is called instead of returning the :contents:.

    If :complain: is True (default), will raise an AssertionError if
    :filename: was not opened in the enclosed block. A NotMocked
    exception will be raised if open() was called with a file that was
    not mocked by mock_open.

    """
    open_files = set()

    def mock_file(*args, encoding=None):
        """Mocked open() function

        Takes the same arguments as the open() function.

        """
        if args[0] == filename:
            if exception is None:
                file_ = io.StringIO(contents)
                file_.name = filename
            else:
                raise exception  # false positive; pylint: disable=raising-bad-type
        else:
            mocked_file.stop()
            file_ = open(*args, encoding=encoding)  # pylint: disable=consider-using-with
            mocked_file.start()
        open_files.add(file_.name)
        return file_

    mocked_file = unittest.mock.patch("builtins.open", mock_file)
    mocked_file.start()
    try:
        yield
    except NotMocked as error:
        if error.filename != filename:
            raise
    mocked_file.stop()
    try:
        open_files.remove(filename)
    except KeyError as error:
        if complain:
            raise AssertionError(f"The file {filename} was not opened.") from error
    for f_name in open_files:
        if complain:
            raise NotMocked(f_name)
