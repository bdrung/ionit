# The MIT License (MIT)

# Copyright (c) 2013 Ionuț Arțăriși <ionut@artarisi.eu>

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

"""Test mock_open()

Origin: https://github.com/mapleoin/mock_open
"""

import collections
import unittest
import unittest.mock

from .mock_open import NotMocked, mock_open


class OrderedSet(collections.UserList):  # pylint: disable=too-many-ancestors
    """set subclass that remembers the order entries were added"""

    def add(self, element):
        """Add given element to set"""
        if element not in self.data:
            self.data.append(element)


class MockTest(unittest.TestCase):
    """Test mock_open()"""

    def test_open_same_file_twice(self):
        """Test opening the same mocked file twice"""
        with mock_open("test_file", "foo"):
            with open("test_file", encoding="utf-8") as first:
                with open("test_file", encoding="utf-8") as second:
                    self.assertEqual(first.read(), second.read())
                    first.seek(0)
                    self.assertEqual("foo", first.read())

    def test_file_not_open_mocked(self):
        """Test not opening the mocked file"""
        with self.assertRaises(AssertionError):
            with mock_open("file"):
                pass

    @unittest.mock.patch("builtins.set", OrderedSet)
    def test_file_open_not_mocked(self):
        """Test opening a not mocked file"""
        with self.assertRaises(NotMocked):
            with mock_open("file1", "foo"):
                with mock_open("file2", "foo"):
                    with open(__file__, encoding="utf-8"):
                        with open("file1", encoding="utf-8") as mocked_file1:
                            with open("file2", encoding="utf-8") as mocked_file2:
                                self.assertEqual(mocked_file1.read(), mocked_file2.read())

    def test_raise_exception(self):
        """Test raising an exception on mocked open()"""
        with self.assertRaises(PermissionError):
            with mock_open("file", exception=PermissionError(13, "Permission denied")):
                open("file", encoding="utf-8")  # pylint: disable=consider-using-with
