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

"""Helper function for writing ionit plugins"""

import logging


class FunctionCollector:
    """Collect functions for the Jinja renderer"""

    functions = {}

    def __new__(cls):
        # Singleton
        if not hasattr(cls, "instance") or not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def clear(self):
        """Reset the list of functions

        Call this method between importing different modules.
        """
        self.functions = {}

    def function(self, func):
        """Function decorator to collect functions for Jinja rendering

        Functions using this decorator will be collected and ionit will
        use them in the context to make these functions available for
        the Jinja template rendering.

        """
        logger = logging.getLogger(__name__)
        logger.debug("Collecting function '%s'.", func.__name__)
        self.functions[func.__name__] = func
        return func


function = FunctionCollector().function  # false positive, pylint: disable=invalid-name
