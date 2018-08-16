# Copyright (C) 2018, Benjamin Drung <benjamin.drung@profitbricks.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""Test ionit"""

import os
import re
import unittest

from ionit import collect_context, main, render_templates

from .mock_open import mock_open

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(TESTS_DIR, "config")
TEMPLATE_DIR = os.path.join(TESTS_DIR, "template")


class TestCollectContext(unittest.TestCase):
    """
    This unittest class tests collecting the context.
    """

    def test_collect_function(self):
        """Test: Run collect_context("tests/config/function")"""
        failures, context = collect_context(os.path.join(CONFIG_DIR, "function"))
        self.assertEqual(failures, 0)
        self.assertEqual(set(context.keys()), set(["answer_to_all_questions"]))
        self.assertEqual(context["answer_to_all_questions"](), 42)

    def test_collect_static_context(self):
        """Test: Run collect_context("tests/config/static")"""
        self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "static")), (0, {
            "first": 1,
            "second": 2,
        }))

    def test_context_stacking(self):
        """Test: Run collect_context("tests/config/stacking")"""
        self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "stacking")), (0, {
            "big_number": 1071,
            "small_number": 7,
        }))

    def test_empty_python_file(self):
        """Test: Run collect_context("tests/config/empty")"""
        with self.assertLogs("ionit", level="WARNING") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "empty")), (0, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], (
                "WARNING:ionit:Python module '[^']+config/empty/empty.py' does "
                "neither define a collect_context function, nor export functions "
                r"\(using the ionit_plugin.function decorator\)."))

    def test_ignoring_additional_files(self):
        """Test: Run collect_context("tests/config/additional-file")"""
        with self.assertLogs("ionit", level="INFO") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "additional-file")),
                             (0, {"key": "value"}))
            self.assertEqual(len(context_manager.output), 2)
            self.assertRegex(context_manager.output[0], (
                "INFO:ionit:Skipping configuration file '[^']*config/additional-file/echo', "
                "because it does not end with .*"))

    def test_invalid_json(self):
        """Test: Run collect_context("tests/config/invalid-json")"""
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "invalid-json")), (1, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], (
                "ERROR:ionit:Failed to read JSON from '[^']*config/invalid-json/invalid.json': "
                r"Expecting property name enclosed in double quotes: line 3 column 1 \(char 22\)"))

    def test_invalid_python(self):
        """Test: Run collect_context("tests/config/invalid-python")"""
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "invalid-python")), (1, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], re.compile(
                "ERROR:ionit:Importing Python module '[^']*config/invalid-python/invalid.py' "
                r"failed:\n.*\nValueError: invalid literal for int\(\) with base 10: 'invalid'$",
                flags=re.DOTALL))

    def test_invalid_yaml(self):
        """Test: Run collect_context("tests/config/invalid-yaml")"""
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "invalid-yaml")), (1, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], (
                "ERROR:ionit:Failed to read YAML from '[^']*config/invalid-yaml/invalid.yaml': "
                r"mapping values are not allowed here\s+"
                r"in \"\S*config/invalid-yaml/invalid.yaml\", line 1, column 14"))

    def test_missing_directory(self):
        """Test: Non-existing context directory"""
        with self.assertLogs("ionit", level="WARNING") as context_manager:
            self.assertEqual(collect_context(os.path.join(TESTS_DIR, "non-existing-directory")),
                             (0, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], (
                r"WARNING:ionit:Failed to read configuration directory: \[Errno 2\] "
                r"No such file or directory: '\S*non-existing-directory'"))

    def test_non_dict_context(self):
        """Test failure for collect_context("tests/config/non-dict")"""
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "non-dict")), (1, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], (
                "ERROR:ionit:Failed to update context with content from "
                r"'\S*config/non-dict/invalid.yaml': dictionary update sequence "
                "element #0 has length 1; 2 is required"))

    def test_python_module(self):
        """Test: Run collect_context("tests/config/python")"""
        self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "python")), (0, {
            "small": 42,
            "big": 8000,
        }))

    def test_raise_exception(self):
        """Test failure for collect_context("tests/config/exception")"""
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(collect_context(os.path.join(CONFIG_DIR, "exception")), (1, {}))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], re.compile(
                r"ERROR:ionit:Calling collect_context\(\) from '\S*config/exception/exception.py' "
                "failed:\n.*\nException: Oops.$", flags=re.DOTALL))


class TestRendering(unittest.TestCase):
    """
    This unittest class tests rendering the templates.
    """

    def test_attribution_error(self):
        """Test: Run render_templates("tests/template/attribution-error")"""
        template_dir = os.path.join(TEMPLATE_DIR, "attribution-error")
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(render_templates(template_dir, {}, "jinja"), 1)
            self.assertFalse(os.path.exists(os.path.join(template_dir, "error")))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], re.compile(
                r"^ERROR:ionit:Failed to render '\S*template/attribution-error/error.jinja':\n.*\n"
                "AttributeError: 'dict_items' object has no attribute 'items'$", flags=re.DOTALL))

    def test_missing_context(self):
        """Test: Missing context for render_templates("tests/template/static")"""
        template_dir = os.path.join(TEMPLATE_DIR, "static")
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(render_templates(template_dir, {"second": "B"}, "jinja"), 1)
            self.assertFalse(os.path.exists(os.path.join(template_dir, "counting")))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], re.compile(
                r"^ERROR:ionit:Failed to render '\S*template/static/counting.jinja':\n.*\n"
                "jinja2.exceptions.UndefinedError: 'first' is undefined$", flags=re.DOTALL))

    def test_render_function(self):
        """Test: Run render_templates("tests/template/function")"""
        template_dir = os.path.join(TEMPLATE_DIR, "function")
        try:
            context = {"answer_to_all_questions": lambda: 42}
            self.assertEqual(render_templates(template_dir, context, "jinja"), 0)
            with open(os.path.join(template_dir, "Document")) as document_file:
                self.assertEqual(document_file.read(), (
                    "The answer to the Ultimate Question of Life, The Universe, "
                    "and Everything is 42.\n"))
        finally:
            os.remove(os.path.join(template_dir, "Document"))

    def test_render_invalid(self):
        """Test: Run render_templates("tests/template/invalid")"""
        template_dir = os.path.join(TEMPLATE_DIR, "invalid")
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            self.assertEqual(render_templates(template_dir, {}, "jinja"), 1)
            self.assertFalse(os.path.exists(os.path.join(template_dir, "invalid")))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], re.compile(
                r"ERROR:ionit:Failed to load template '\S*template/invalid/invalid.jinja':\n.*\n"
                "jinja2.exceptions.TemplateSyntaxError: unexpected 'end of template'$",
                flags=re.DOTALL))

    def test_render_static(self):
        """Test: Run render_templates("tests/template/static")"""
        template_dir = os.path.join(TEMPLATE_DIR, "static")
        try:
            context = {"first": "A", "second": "B"}
            self.assertEqual(render_templates(template_dir, context, "jinja"), 0)
            with open(os.path.join(template_dir, "counting")) as counting_file:
                self.assertEqual(counting_file.read(), "Counting:\n* A\n* B\n* 3\n")
        finally:
            os.remove(os.path.join(template_dir, "counting"))

    def test_render_write_protected(self):
        """Test: Run render_templates("tests/template/static"), but write protected"""
        template_dir = os.path.join(TEMPLATE_DIR, "static")
        context = {"first": "A", "second": "B"}
        with self.assertLogs("ionit", level="ERROR") as context_manager:
            with mock_open(os.path.join(template_dir, "counting"),
                           exception=PermissionError(13, "Permission denied"), complain=False):
                self.assertEqual(render_templates(template_dir, context, "jinja"), 1)
            self.assertFalse(os.path.exists(os.path.join(template_dir, "counting")))
            self.assertEqual(len(context_manager.output), 1)
            self.assertRegex(context_manager.output[0], (
                r"ERROR:ionit:Failed to write rendered template to '\S*template/static/counting': "
                r"\[Errno 13\] Permission denied"))


class TestMain(unittest.TestCase):
    """Test main function"""
    def test_main_static(self):
        """Test main() with static context"""
        template_dir = os.path.join(TEMPLATE_DIR, "static")
        try:
            self.assertEqual(main(["-c", os.path.join(TESTS_DIR, "config/static"), "-t",
                                   template_dir]), 0)
            with open(os.path.join(template_dir, "counting")) as counting_file:
                self.assertEqual(counting_file.read(), "Counting:\n* 1\n* 2\n* 3\n")
        finally:
            os.remove(os.path.join(template_dir, "counting"))
