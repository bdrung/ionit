---
date: 2018-08-13
footer: ionit
header: "ionit's Manual"
layout: page
license: 'Licensed under the ISC license'
section: 1
title: IONIT
---

# NAME

ionit - Render configuration files from Jinja templates

# SYNOPSIS

**ionit** [**OPTIONS**]

# DESCRIPTION

**ionit** is a simple and small configuration templating tool. It collects a
context and renders Jinja templates in a given directory. The context can be
either static JSON or YAML files or dynamic Python files. Python files can also
define functions passed through to the rendering.

The context filenames needs to end with *.json* for JSON, *.py* for Python,
and *.yaml* for YAML. The context files are read in alphabetical order. If the
same key is defined by multiple context files, the file that is read later takes
precedence. It is recommended to prefix the files with a number in case the
order is relevant.

**ionit** comes with an early boot one shot service that is executed before the
networking service which allows one to generate configurations files for the
networking and other services before they are started. In this regard, ionit can
act as tiny stepbrother of cloud-init.

# OPTIONS

**-c** */path/to/config*, **--config** */path/to/config*
:    Configuration directory containing context for rendering (default:
*/etc/ionit*)

**-t** */path/to/templates*, **--templates** */path/to/templates*
:    Directory to search for Jinja templates (default: */etc*)

**-e** *TEMPLATE_EXTENSION*, **--template-extension** *TEMPLATE_EXTENSION*
:    Extension to look for in template directory (default: *jinja*)

**--debug**
:    Print debug output

**-q**, **--quiet**
:    Decrease output verbosity to warnings and errors.

# PYTHON MODULES

Python modules can define a *collect_context* function. This function is called
by ionit and the current context is passed as parameter. The current context can
be used to derive more context information, but this variable should not be
modified. *collect_context* must return a dictionary (can be empty) or raise an
exception, which will be caught by ionit.

Python modules can also define functions which can be called from the Jinja
template on rendering. Use the *ionit_plugin.function* decorator to mark the
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

# AUTHOR

Benjamin Drung <bdrung@posteo.de>
