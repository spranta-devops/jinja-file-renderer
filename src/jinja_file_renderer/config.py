# SPDX-FileCopyrightText: 2024 Gerd Aschbrenner
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import logging
import os
from enum import Enum
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

from dotenv import dotenv_values

"""
All configuration settings of the JinjaFileRenderer are collected in the JinjaFileRendererConfig object.
"""

RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON = Path('os.env')
DEFAULT_DOTENV_FILES: list[Path] = list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON, Path('.env')])


class TargetDirContentDeletionMode(Enum):
    DO_DELETE = 1
    DO_NOT_DELETE = 2


class JinjaFileRendererConfig:
    _logger: Logger = logging.getLogger(__name__)
    dotenv_files: list[Path] = DEFAULT_DOTENV_FILES
    source_dir: Path
    target_dir: Path
    target_dir_content_deletion_mode: TargetDirContentDeletionMode = TargetDirContentDeletionMode.DO_NOT_DELETE

    template_vars: dict[str, str]

    def __init__(
        self,
        source_dir: Path,
        target_dir: Path,
        target_dir_content_deletion_mode: TargetDirContentDeletionMode,
        dotenv_files: list[Path],
    ):
        if dotenv_files is None:
            err_message1: str = 'Expected a value for the argument dotenv_files.'
            raise ValueError(err_message1)
        if source_dir is None:
            err_message2: str = 'Expected a value for the argument source_dir.'
            raise ValueError(err_message2)
        if target_dir is None:
            err_message3: str = 'Expected a value for the argument target_dir.'
            raise ValueError(err_message3)
        if target_dir_content_deletion_mode is None:
            err_message4: str = 'Expected a value for the argument target_dir_content_deletion_mode.'
            raise ValueError(err_message4)

        self.dotenv_files = dotenv_files
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.target_dir_content_deletion_mode = target_dir_content_deletion_mode

        collected_vars: dict = {}
        if len(dotenv_files) == 0:
            self._logger.warning('No dotenv files configured. Their will not be any variable for templating.')
        for dotenv_file in dotenv_files:
            if dotenv_file == RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON:
                collected_vars = JinjaFileRendererConfig._collect_os_environ_vars(collected_vars)
            else:
                collected_vars = JinjaFileRendererConfig._collect_dotenv_vars(collected_vars, dotenv_file)
        if len(collected_vars) == 0:
            self._logger.warning(
                'No variables for templating found. Please add "os.environ" or an existing dotenv file.'
            )
        self.template_vars = collected_vars

    @staticmethod
    def _collect_dotenv_vars(collected: dict, dotenv_file: Path) -> dict:
        if collected is None:
            err_message1: str = 'Expected a value for the argument collected.'
            raise ValueError(err_message1)
        if dotenv_file is None:
            err_message2: str = 'Expected a value for the argument dotenv_file.'
            raise ValueError(err_message2)
        ret: dict = collected.copy()
        if dotenv_file.exists() and dotenv_file.is_file():
            dotenv_result: dict[str, str | None] = dotenv_values(dotenv_file)
            dotenv_keys = dotenv_result.keys()
            if len(dotenv_keys) == 0:
                JinjaFileRendererConfig._logger.debug('Found dotenv file %s, but it is empty.', dotenv_file)
            else:
                JinjaFileRendererConfig._logger.debug(
                    'Found dotenv file "%s" with %s entries.',
                    dotenv_file,
                    len(dotenv_keys),
                )
                for name in dotenv_keys:
                    value: str | None = dotenv_result.get(name)
                    if value is None:
                        if name in ret:
                            JinjaFileRendererConfig._logger.debug(
                                'Removing template variable %s = %s, because of overwrite from dotenv files "%s" '
                                'entry without value.',
                                name,
                                value,
                                dotenv_file,
                            )
                            del ret[name]
                        else:
                            JinjaFileRendererConfig._logger.debug(
                                'Ignoring template variable %s from dotenv file "%s", because no value is set.',
                                name,
                                dotenv_file,
                            )
                    else:
                        if name in ret:
                            JinjaFileRendererConfig._logger.debug(
                                'Overwriting template variable value %s with dotenv files "%s" entry %s = %s',
                                ret[name],
                                dotenv_file,
                                name,
                                value,
                            )
                        else:
                            JinjaFileRendererConfig._logger.debug(
                                'Registering template variable from dotenv files "%s" entry %s = %s',
                                dotenv_file,
                                name,
                                value,
                            )
                        ret[name] = value
        else:
            JinjaFileRendererConfig._logger.debug(
                'Did not found the dotenv file "%(dotenv_file)".',
                extra={'dotenv_file': dotenv_file},
            )
        return ret

    @staticmethod
    def _collect_os_environ_vars(collected: dict) -> dict:
        if collected is None:
            err_message: str = 'Expected a value for the argument collected.'
            raise ValueError(err_message)
        ret: dict = collected.copy()
        for name, value in os.environ.items():
            if value is None:
                if name in ret:
                    JinjaFileRendererConfig._logger.debug(
                        'Removing template variable %s = %s, because of overwrite from environment variable '
                        'without value',
                        name,
                        ret[name],
                    )
                    del ret[name]
                else:
                    JinjaFileRendererConfig._logger.debug(
                        'Ignoring template variable %s from environment, because no value is set.',
                        name,
                    )
            else:
                if name in ret:
                    JinjaFileRendererConfig._logger.debug(
                        'Overwriting template variable value %s with environment variable %s = %s',
                        ret[name],
                        name,
                        value,
                    )
                else:
                    JinjaFileRendererConfig._logger.debug(
                        'Registering template variable from environment variable %s = %s',
                        name,
                        value,
                    )
                ret[name] = value
        return ret

    @classmethod
    def from_argparse(cls, args: Namespace):
        """
        Instantiation with values from argparse modul.
        :param args: argparse.ArgumentParser.parse_args()
        :return: JinjaFileRendererConfig
        """
        if args.should_delete_target_dir_content:
            target_dir_content_deletion_mode = TargetDirContentDeletionMode.DO_DELETE
        else:
            target_dir_content_deletion_mode = TargetDirContentDeletionMode.DO_NOT_DELETE
        return JinjaFileRendererConfig(
            source_dir=args.source_dir,
            target_dir=args.target_dir,
            target_dir_content_deletion_mode=target_dir_content_deletion_mode,
            dotenv_files=list[Path](args.dotenv_files),
        )

    def to_string(self) -> str:
        """
        String representation for logging (or debugging).
        """
        return (
            'JinjaFileRendererConfig['
            f'\n  source_dir={self.source_dir}'
            f'\n  target_dir={self.target_dir}'
            f'\n  dotenv_files={self.dotenv_files}'
            f'\n  target_dir_content_deletion_mode={self.target_dir_content_deletion_mode}'
            '\n]'
        )
