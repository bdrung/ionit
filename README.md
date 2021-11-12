[![CI](https://img.shields.io/github/workflow/status/bdrung/ionit/CI)](https://github.com/bdrung/ionit/actions/workflows/ci.yaml)
[![Codecov](https://img.shields.io/codecov/c/github/bdrung/ionit)](https://codecov.io/gh/bdrung/ionit)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![License: ISC](https://img.shields.io/badge/license-ISC-blue)](LICENSE)
[![Debian package](https://img.shields.io/debian/v/ionit/unstable)](https://tracker.debian.org/pkg/ionit)
[![PyPI project](https://img.shields.io/pypi/v/ionit)](https://pypi.org/project/ionit/)
[![Ubuntu package](https://img.shields.io/ubuntu/v/ionit)](https://launchpad.net/ubuntu/+source/ionit)

ionit
=====

ionit is a simple and small configuration templating tool. It collects a context
and renders Jinja templates in a given directory. The context can be either
static JSON or YAML files or dynamic Python files. Python files can also define
functions passed through to the rendering.

The context filenames needs to end with `.json` for JSON, `.py` for Python,
and `.yaml` for YAML. The context files are read in alphabetical order. If the
same key is defined by multiple context files, the file that is read later takes
precedence. It is recommended to prefix the files with a number in case the
order is relevant.

ionit comes with an early boot one shot service that is executed before the
networking service which allows one to generate configurations files for the
networking and other services before they are started. In this regard, ionit can
act as tiny stepbrother of cloud-init.

Python modules
==============

Python modules can define a `collect_context` function. This function is called
by ionit and the current context is passed as parameter. The current context can
be used to derive more context information, but this variable should not be
modified. `collect_context` must return a dictionary (can be empty) or raise an
exception, which will be caught by ionit.

Python modules can also define functions which can be called from the Jinja
template on rendering. Use the `ionit_plugin.function` decorator to mark the
functions to export.

Note that the functions names should not collide with other keys from the
context. If one Python module defines a function and a value in the context
with the same name, the value in the context will take precedence.

An example Python module might look like:

```python
import ionit_plugin


@ionit_plugin.function
def double(value):
    return 2 * value


@ionit_plugin.function
def example_function():
    return "Lorem ipsum"


def collect_context(current_context):
    return {"key": "value"}
```

Prerequisites
=============

* Python >= 3.6
* Python modules:
  * jinja2
  * PyYAML or ruamel.yaml
* pandoc (to generate `ionit.1` man page from `ionit.1.md`)

The test cases have additional requirements:

* black
* flake8
* isort
* pylint

Examples
========

Static context
--------------

This example is taken from one test case and demonstrates how ionit will collect
the context from one JSON and one YAML file and renders one template:

```
user@host:~/ionit$ cat tests/config/static/first.json
{"first": 1}
user@host:~/ionit$ cat tests/config/static/second.yaml
---
second: 2
user@host:~/ionit$ cat tests/template/static/counting.jinja
Counting:
* {{ first }}
* {{ second }}
* 3
user@host:~/ionit$ ./ionit -c tests/config/static -t tests/template/static
2018-08-08 17:39:06,956 ionit INFO: Reading configuration file 'tests/config/static/first.json'...
2018-08-08 17:39:06,956 ionit INFO: Reading configuration file 'tests/config/static/second.yaml'...
2018-08-08 17:39:06,960 ionit INFO: Rendered 'tests/template/static/counting.jinja' to 'tests/template/static/counting'.
user@host:~/ionit$ cat tests/template/static/counting
Counting:
* 1
* 2
* 3
```

Python functions
----------------

This example is taken from one test case and demonstrates how Python functions
can be defined to be used when rendering:

```
user@host:~/ionit$ cat tests/config/function/function.py
import ionit_plugin


@ionit_plugin.function
def answer_to_all_questions():
    return 42
user@host:~/ionit$ cat tests/template/function/Document.jinja
The answer to the Ultimate Question of Life, The Universe, and Everything is {{ answer_to_all_questions() }}.
user@host:~/ionit$ ./ionit -c tests/config/function -t tests/template/function
2018-08-13 11:58:16,905 ionit INFO: Loading Python module 'function' from 'tests/config/function/function.py'...
2018-08-13 11:58:16,909 ionit INFO: Rendered 'tests/template/function/Document.jinja' to 'tests/template/function/Document'.
user@host:~/ionit$ cat tests/template/function/Document
The answer to the Ultimate Question of Life, The Universe, and Everything is 42.
```

Contributing
============

Contributions are welcome. The source code has 100% test coverage, which should
be preserved. So please provide a test case for each bugfix and one or more
test cases for each new feature. Please follow
[How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
for writing good commit messages.

Creating releases
=================

This project uses [semantic versioning](https://semver.org/). To create a
release, increase the version in `setup.py` and document the noteworthy changes
in [NEWS.md](./NEWS.md). Then commit the changes and tag the release:

```
git commit -sm "Release ionit $(./setup.py --version)" NEWS.md setup.py
git tag v$(./setup.py --version)
```

The xz-compressed release tarball can be generated by running:
```
name="ionit-$(./setup.py --version)"
git archive --prefix="$name/" HEAD | xz -c9 > "../$name.tar.xz"
gpg --output "../$name.tar.xz.asc" --armor --detach-sign "../$name.tar.xz"
```

The package for PyPI can be built and uploaded by running:

```
pyproject-build --no-isolation
twine upload --repository pypi dist/*
```
