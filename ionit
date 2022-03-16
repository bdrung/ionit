#!/usr/bin/python3

# Copyright (C) 2018-2022, Benjamin Drung <bdrung@posteo.de>
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

"""Render configuration files from Jinja templates"""

import argparse
import importlib.util
import json
import logging
import os
import sys

import jinja2

import ionit_plugin

try:
    import yaml
except ImportError:
    from ruamel import yaml


DEFAULT_CONFIG = "/etc/ionit"
DEFAULT_TEMPLATES_DIRECTORY = "/etc"
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"
SCRIPT_NAME = "ionit"


class PythonModuleException(Exception):
    """Exception raised when loading a Python context file fails"""


def load_python_plugin(file_path, current_context):
    """Collect context from given Python module

    The specified Python file needs to be a valid plug-in which provides
    a collect_context function that takes the current context as parameter
    and returns a dict containing the context.
    """
    logger = logging.getLogger(SCRIPT_NAME)
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    logger.info("Loading Python module '%s' from '%s'...", module_name, file_path)
    function_collector = ionit_plugin.FunctionCollector()
    function_collector.clear()
    dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as error:
        logger.exception("Importing Python module '%s' failed:", file_path)
        raise PythonModuleException() from error
    finally:
        sys.dont_write_bytecode = dont_write_bytecode

    context = function_collector.functions.copy()
    if hasattr(module, "collect_context"):
        try:
            new_context = module.collect_context(current_context)
        except Exception as error:
            logger.exception("Calling collect_context() from '%s' failed:", file_path)
            raise PythonModuleException() from error
        context.update(new_context)
    elif not context:
        logger.warning(
            "Python module '%s' does neither define a collect_context function, "
            "nor export functions (using the ionit_plugin.function decorator).",
            file_path,
        )

    return context


def get_config_files(paths):
    """Return files for the given paths (could either be files or directories)."""
    logger = logging.getLogger(SCRIPT_NAME)
    files = []
    for path in paths:
        logger.debug("Searching for configuration files in '%s'...", path)
        try:
            if os.path.isfile(path):
                files.append(path)
            else:
                files += sorted([os.path.join(path, f) for f in os.listdir(path)])
        except OSError as error:
            logger.warning("Failed to read configuration directory: %s", error)
    logger.debug("Configuration files: %s", files)
    return files


def collect_context(paths, encoding):
    """Collect context that will be used when rendering the templates"""
    logger = logging.getLogger(SCRIPT_NAME)
    logger.debug("Collecting context...")

    failures = 0
    context = {}

    for file in get_config_files(paths):
        file_context = None
        extension = os.path.splitext(file)[1]
        try:
            if extension == ".json":
                logger.info("Reading configuration file '%s'...", file)
                with open(file, encoding=encoding) as config_file:
                    file_context = json.load(config_file)
            elif extension == ".py":
                file_context = load_python_plugin(file, context)
            elif extension == ".yaml":
                logger.info("Reading configuration file '%s'...", file)
                with open(file, encoding=encoding) as config_file:
                    file_context = yaml.load(config_file, Loader=yaml.SafeLoader)
            else:
                logger.info(
                    "Skipping configuration file '%s', "
                    "because it does not end with '.json', '.py', or '.yaml'.",
                    file,
                )
                continue
        except PythonModuleException:
            failures += 1
            continue
        except (OSError, ValueError, yaml.error.YAMLError) as error:
            types = {".json": "JSON", ".py": "Python code", ".yaml": "YAML"}
            logger.error("Failed to read %s from '%s': %s", types[extension], file, error)
            failures += 1
            continue

        logger.debug("Parsed context from '%s': %s", file, file_context)
        if file_context:
            try:
                context.update(file_context)
            except (TypeError, ValueError) as error:
                logger.debug("Current context: %s", context)
                logger.error("Failed to update context with content from '%s': %s", file, error)
                failures += 1
                continue

    return failures, context


def render_templates(template_dir, context, template_extension, encoding):
    """
    Search in the template directory for template files and render them with the context
    """
    logger = logging.getLogger(SCRIPT_NAME)
    logger.debug("Searching in directory '%s' for Jinja templates...", template_dir)
    failures = 0
    env = jinja2.Environment(
        keep_trailing_newline=True,
        loader=jinja2.FileSystemLoader(template_dir),
        undefined=jinja2.StrictUndefined,
    )
    for name in env.list_templates(extensions=[template_extension]):
        try:
            template = env.get_template(name)
        except jinja2.TemplateError:
            logger.exception("Failed to load template '%s':", os.path.join(template_dir, name))
            failures += 1
            continue

        rendered_filename = os.path.splitext(template.filename)[0]
        logger.debug("Rendering template '%s' to '%s'...", template.filename, rendered_filename)
        try:
            rendered = template.render(context)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to render '%s':", template.filename)
            failures += 1
            continue

        try:
            with open(rendered_filename, "w", encoding=encoding) as output_file:
                output_file.write(rendered)
        except OSError as error:
            logger.error("Failed to write rendered template to '%s': %s", rendered_filename, error)
            failures += 1
            continue

        logger.info("Rendered '%s' to '%s'.", template.filename, rendered_filename)

    return failures


def main(argv):
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        action="append",
        help="Configuration directory/file containing context for rendering "
        f"(default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "-t",
        "--templates",
        action="append",
        help=f"Directory to search for Jinja templates (default: {DEFAULT_TEMPLATES_DIRECTORY})",
    )
    parser.add_argument(
        "-e",
        "--template-extension",
        default="jinja",
        help="Extension to look for in template directory (default: %(default)s)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding of the configuration files and Jinja templates (default: %(default)s)",
    )
    parser.add_argument(
        "--debug",
        dest="log_level",
        help="Print debug output",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="log_level",
        help="Decrease output verbosity to warnings and errors",
        action="store_const",
        const=logging.WARNING,
    )
    args = parser.parse_args(argv)
    if args.config is None:
        args.config = [DEFAULT_CONFIG]
    if args.templates is None:
        args.templates = [DEFAULT_TEMPLATES_DIRECTORY]
    logging.basicConfig(level=args.log_level, format=LOG_FORMAT)
    logger = logging.getLogger(SCRIPT_NAME)

    failures, context = collect_context(args.config, args.encoding)
    logger.debug("Context: %s", context)
    for template in args.templates:
        failures += render_templates(template, context, args.template_extension, args.encoding)
    return failures


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
