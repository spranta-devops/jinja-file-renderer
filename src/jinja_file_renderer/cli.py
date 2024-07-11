# SPDX-FileCopyrightText: 2024 Gerd Aschbrenner
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from jinja_file_renderer.__about__ import __version__
from jinja_file_renderer.config import (
    DEFAULT_DOTENV_FILES,
    JinjaFileRendererConfig,
)
from jinja_file_renderer.renderer import FilenameClashError, JinjaFileRenderer

_logger = logging.getLogger(__name__)

"""
Using the jina-file-renderer from a command line. The parsed arguments are used to create a JinjaFileRendererConfig
(config.py) object for the JinjaFileRenderer (renderer.py).
"""


def _argparse_log_level(log_level_arg: str) -> int:
    """
    argument type validation for argparse
    """
    sanitized_log_level = log_level_arg.upper()
    if sys.version_info < (3, 11):
        if sanitized_log_level == 'CRITICAL':
            log_level = logging.CRITICAL
        elif sanitized_log_level == 'FATAL':
            log_level = logging.FATAL
        elif sanitized_log_level == 'ERROR':
            log_level = logging.ERROR
        elif sanitized_log_level in ['WARN', 'WARNING']:
            log_level = logging.WARNING
        elif sanitized_log_level == 'INFO':
            log_level = logging.INFO
        elif sanitized_log_level == 'DEBUG':
            log_level = logging.DEBUG
        else:
            log_level = None
    else:
        log_level_mapping: dict[str, int] = logging.getLevelNamesMapping()
        log_level: int | None = log_level_mapping.get(sanitized_log_level)
    if log_level is None:
        err_message: str = f'log_level: "{log_level_arg}" is not valid.'
        raise argparse.ArgumentTypeError(err_message)
    return log_level


def _argparse_readable_dir(path_arg: str) -> Path:
    """
    argument type validation for argparse
    """
    path: Path = Path(path_arg)
    if path.exists():
        if path.is_dir():
            if os.access(path, os.R_OK):
                return path
            err_message1: str = f'readable_dir: "{path_arg}" is not readable.'
            raise argparse.ArgumentTypeError(err_message1)
        err_message2: str = f'readable_dir: "{path_arg}" is not a directory.'
        raise argparse.ArgumentTypeError(err_message2)
    err_message3: str = f'readable_dir: "{path_arg}" does not exists.'
    raise argparse.ArgumentTypeError(err_message3)


def _argparse_writeable_dir(path_arg: str) -> Path:
    """
    argument type validation for argparse
    """
    path: Path = Path(path_arg)
    if path.exists():
        if path.is_dir():
            if os.access(path, os.W_OK):
                return path
            err_message1: str = f'writeable_dir: "{path_arg}" is not writeable.'
            raise argparse.ArgumentTypeError(err_message1)
        err_message2: str = f'writeable_dir: "{path_arg}" is not a directory.'
        raise argparse.ArgumentTypeError(err_message2)
    err_message3: str = f'writeable_dir: "{path_arg}" does not exists.'
    raise argparse.ArgumentTypeError(err_message3)


def _argparse_dotenv_file(filepath_arg: str) -> Path:
    """
    argument type validation for argparse
    """
    path: Path = Path(filepath_arg)
    if path.exists():
        if path.is_file():
            if os.access(path, os.R_OK):
                return path
            err_message1: str = f'dotenv_files: "{filepath_arg}" is not readable.'
            raise argparse.ArgumentTypeError(err_message1)
        err_message2: str = f'dotenv_files: "{filepath_arg}" is not a file.'
        raise argparse.ArgumentTypeError(err_message2)
    return path  # add non-existing file, yeah, that's right.


def _parse_arguments(argv: list[str]) -> JinjaFileRendererConfig:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='jinja-file-renderer',
        description='Copying a directory, during which *.jinja files are rendered via Jinja2.',
    )
    parser.add_argument(
        '--version',
        help='Outputs programs version.',
        action='version',
        version='%(prog)s (' + __version__ + ')',
    )
    parser.add_argument(
        '--log-level',
        help='Choose (python logging) log level [DEBUG, INFO, WARNING, ERROR, CRITICAL]. Default is INFO',
        type=_argparse_log_level,
        default=logging.INFO,
        dest='log_level',
        metavar='LOG-LEVEL',
    )
    parser.add_argument(
        '--dotenv-files',
        help='Default is "os.env .env". "os.env" is a reserved filename for OS environment variables. Each entry is '
        'overwriting the values of the previous ones.',
        dest='dotenv_files',
        metavar='FILE',
        type=_argparse_dotenv_file,
        nargs='*',
        default=DEFAULT_DOTENV_FILES,
    )
    parser.add_argument(
        '--delete-target-dir-content',
        help='The content of the target-dir will be deleted before filling it again. Be careful with this option, it '
        'will not ask for permission and the files are lost forever.',
        action='store_true',
        dest='should_delete_target_dir_content',
        default=False,
    )
    parser.add_argument(
        '--source-dir',
        help='The source directory where all files should be copied recursively from.',
        required=True,
        dest='source_dir',
        metavar='DIRECTORY',
        type=_argparse_readable_dir,
    )
    parser.add_argument(
        '--target-dir',
        help='The (empty) target directory where all files should be copied or rendered to.',
        required=True,
        dest='target_dir',
        metavar='DIRECTORY',
        type=_argparse_writeable_dir,
    )

    args: argparse.Namespace = parser.parse_args(argv)
    logging.basicConfig(encoding='utf-8', level=args.log_level)
    return JinjaFileRendererConfig.from_argparse(args)


def main(argv: list[str] | None = None):
    if argv is None:  # Has to be optional, so that "hatch run jinja-file-renderer" works
        argv = sys.argv[1:]
    config: JinjaFileRendererConfig = _parse_arguments(argv)
    renderer: JinjaFileRenderer = JinjaFileRenderer(config)
    _logger.debug('jinja_file_renderer %s running with options (arguments):\n%s', __version__, config.to_string())
    try:
        renderer.copy_and_render_files()
    except FilenameClashError as ex:
        print(str(ex), file=sys.stderr)
        sys.exit(1)


def run_script(name: str):
    """Act like a script if we were invoked like a script."""
    if name == '__main__':
        sys.exit(main(sys.argv[1:]))


run_script(__name__)
