# SPDX-FileCopyrightText: 2024 Gerd Aschbrenner
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import logging
import sys

from jinja_file_renderer.__about__ import __version__

_logger = logging.getLogger(__name__)

"""
Using the jina-file-renderer from a command line.
"""


def cli(argv: list[str]):
    _logger.debug('jinja_file_renderer %s running', __version__)


def main():
    cli(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
