# SPDX-FileCopyrightText: 2024 Gerd Aschbrenner
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import logging
import os
import shutil
from logging import Logger
from os import PathLike
from pathlib import Path

import jinja2
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template, select_autoescape

from jinja_file_renderer.config import JinjaFileRendererConfig, TargetDirContentDeletionMode

"""
The JinjaFileRenderer needs a JinjaFileRendererConfig (config.py) to create a JinjaFileRendererEnvironment used to
render the *.jinja files.
"""

JINJA_FILENAME_SUFFIX: str = '.jinja'


class TemplateVariableUndefinedError(Exception):
    """Raised when a template uses an undefined variable (without default filter)."""

    template_file: PathLike
    variable_name: str

    def __init__(self, template_file: PathLike, variable_name: str):
        self.template_file = template_file
        self.variable_name = variable_name
        super().__init__(f'The template_file "{template_file}" uses the undefined variable "{variable_name}".')


class JinjaFileRendererEnvironment:
    """
    Provides a jinja2 Environment for rendering the *.jinja files.
    """

    _logger: Logger = logging.getLogger(__name__)
    _config: JinjaFileRendererConfig
    _environment: Environment

    def __init__(self, config: JinjaFileRendererConfig):
        if config is None:
            err_message: str = 'Expected a value for the argument config.'
            raise ValueError(err_message)
        self._config = config
        self._environment = Environment(
            loader=FileSystemLoader(config.source_dir),
            keep_trailing_newline=True,
            undefined=StrictUndefined,
            autoescape=select_autoescape(
                [
                    'html' + JINJA_FILENAME_SUFFIX,
                    'htm' + JINJA_FILENAME_SUFFIX,
                    'xhtml' + JINJA_FILENAME_SUFFIX,
                ]
            ),
        )
        template_vars = {}
        for name, value in os.environ.items():
            JinjaFileRendererEnvironment._logger.debug(
                'Registering template variable from environment variable %s = %s',
                name,
                value,
            )
            template_vars[name] = value
        self.__template_vars = template_vars

    def render(self, file: Path) -> str:
        template: Template = self._environment.get_template(str(file))
        try:
            return template.render(self.__template_vars)
        except jinja2.exceptions.UndefinedError as ue:
            varname: str = ''
            if ue.message is None:
                varname = '!!UNKNOWN!!'
            else:
                first_word: str = ue.message.split()[0] or ''
                varname = first_word.strip("'")
            raise TemplateVariableUndefinedError(file, varname) from ue


class TargetDirNotEmptyError(Exception):
    """Raised when the target_dir is not empty."""

    target_dir: PathLike

    def __init__(self, target_dir: PathLike):
        self.target_dir = target_dir
        super().__init__(f'The target_dir "{target_dir}" is not empty.')


class FilenameClashError(Exception):
    """
    Raised when a jinja template file (example.txt.jinja) and a non-template file (example.txt) will result to the same
    filename in the target-dir.
    """

    source_dir: PathLike
    template_file: PathLike
    non_template_file: PathLike

    def __init__(self, source_dir: PathLike, template_file: PathLike, non_template_file: PathLike):
        if source_dir is None:
            err_message1: str = 'Expected a value for the argument source_dir.'
            raise ValueError(err_message1)
        if template_file is None:
            err_message2: str = 'Expected a value for the argument template_file.'
            raise ValueError(err_message2)
        if non_template_file is None:
            err_message3: str = 'Expected a value for the argument non_template_file.'
            raise ValueError(err_message3)
        self.source_dir = source_dir
        self.template_file = template_file
        self.non_template_file = non_template_file
        super().__init__(
            f'The filename of the template file "{template_file}" clashes with the non-template file '
            f'"{non_template_file}".'
        )


class JinjaFileRenderer:
    _logger: Logger = logging.getLogger(__name__)
    _config: JinjaFileRendererConfig

    def __init__(self, config: JinjaFileRendererConfig):
        if config is None:
            err_message: str = 'Expected a value for the argument config.'
            raise ValueError(err_message)
        self._config = config

    @staticmethod
    def _delete_directory_content(directory: Path) -> None:
        if directory is None:
            err_message1: str = 'Expected a value for the argument directory.'
            raise ValueError(err_message1)
        if not directory.exists():
            err_message2: str = f'The directory {directory} does not exist.'
            raise ValueError(err_message2)
        if not directory.is_dir():
            err_message3: str = f'The directory {directory} is not a directory.'
            raise ValueError(err_message3)

        if not any(directory.iterdir()):
            JinjaFileRenderer._logger.debug(
                'The directory "%s" is already empty. No files or directories to delete.',
                directory,
            )
        else:
            JinjaFileRenderer._logger.info(
                'The directory is not empty. Going to delete the directory content of: %s',
                directory,
            )
            for path in directory.iterdir():
                if path.is_file():
                    JinjaFileRenderer._logger.debug('Going to delete the file: %s', path)
                    path.unlink()
                elif path.is_dir():
                    JinjaFileRenderer._logger.debug('Going to delete the directory: %s', path)
                    shutil.rmtree(path)

    @staticmethod
    def _calc_source_file_path_without_source_dir(source_dir: Path, source_file_path: Path) -> Path:
        if source_dir is None:
            err_message1: str = 'Expected a value for the argument source_dir.'
            raise ValueError(err_message1)
        if source_file_path is None:
            err_message2: str = 'Expected a value for the argument source_file_path.'
            raise ValueError(err_message2)
        if len(str(source_dir)) > len(str(source_file_path)):
            err_message3: str = (
                f'Expected value of source_file_path ({source_file_path}) is longer than source_dir ({source_dir}).'
            )
            raise ValueError(err_message3)

        return Path(str(source_file_path).removeprefix(str(source_dir)).removeprefix(os.path.sep))

    @staticmethod
    def _calc_target_file_path(config: JinjaFileRendererConfig, source_file: Path) -> Path:
        if config is None:
            err_message1: str = 'Expected a value for the argument config.'
            raise ValueError(err_message1)
        if source_file is None:
            err_message2: str = 'Expected a value for the argument source_file.'
            raise ValueError(err_message2)
        source_filename: str = source_file.name
        if source_filename.endswith(JINJA_FILENAME_SUFFIX):
            source_filename = source_filename.removesuffix(JINJA_FILENAME_SUFFIX)
            if source_filename is None or len(source_filename) == 0:
                err_message3: str = (
                    f'The source_filename ({source_file}) would be empty after removing the '
                    f'"{JINJA_FILENAME_SUFFIX}" suffix.'
                )
                raise ValueError(err_message3)

        target_path: Path = JinjaFileRenderer._calc_target_subdir(config, source_file.parent)
        target_file: Path = target_path.joinpath(source_filename)
        if str(target_file) == str(config.target_dir):  # should be unreachable code
            err_message4: str = f'Expected target_file != config.target_dir, but is same: {target_file}'
            raise ValueError(err_message4)
        return target_file

    @staticmethod
    def _calc_target_subdir(config: JinjaFileRendererConfig, source_subdir: Path) -> Path:
        if config is None:
            err_message1: str = 'Expected a value for the argument config.'
            raise ValueError(err_message1)
        if source_subdir is None:
            err_message2: str = 'Expected a value for the argument source_subdir.'
            raise ValueError(err_message2)
        if os.path.sep is None:  # should be unreachable code
            err_message3: str = 'Expected a value for os.path.sep.'
            raise ValueError(err_message3)
        source_subdir_without_source_dir: str = (
            str(source_subdir).removeprefix(str(config.source_dir)).removeprefix(os.path.sep)
        )
        if source_subdir_without_source_dir == str(config.source_dir):  # should be unreachable code
            err_message4: str = (
                f'Expected value of source_subdir_without_source_dir is not the same of '
                f'config.source_dir ({config.source_dir}).'
            )
            raise ValueError(err_message4)

        target_subdir: Path = config.target_dir.joinpath(source_subdir_without_source_dir)
        if str(target_subdir) == source_subdir_without_source_dir:  # should be unreachable code
            err_message5: str = (
                f'Expected value of target_subdir is not the same of '
                f'source_subdir_without_source_dir ({target_subdir}).'
            )
            raise ValueError(err_message5)
        if str(target_subdir) == source_subdir_without_source_dir:  # should be unreachable code
            err_message6: str = (
                f'Expected value of target_subdir is not the same of '
                f'source_subdir_without_source_dir ({target_subdir}).'
            )
            raise ValueError(err_message6)
        return target_subdir

    @staticmethod
    def _handle_file(
        renderer: JinjaFileRendererEnvironment,
        config: JinjaFileRendererConfig,
        root: str,
        source_file: str,
    ) -> None:
        if renderer is None:
            err_message1: str = 'Expected a value for the argument renderer.'
            raise ValueError(err_message1)
        if config is None:
            err_message2: str = 'Expected a value for the argument config.'
            raise ValueError(err_message2)
        if root is None:
            err_message3: str = 'Expected a value for the argument root.'
            raise ValueError(err_message3)
        if source_file is None:
            err_message4: str = 'Expected a value for the argument source_file.'
            raise ValueError(err_message4)

        source_file_path: Path = Path(root).joinpath(source_file)
        if source_file_path.name.endswith(JINJA_FILENAME_SUFFIX):
            target_file_path = JinjaFileRenderer._calc_target_file_path(config, source_file_path)
            JinjaFileRenderer._logger.debug(
                'Found file "%s", going to render to: %s',
                source_file_path,
                target_file_path,
            )

            rendered_file_content = renderer.render(
                JinjaFileRenderer._calc_source_file_path_without_source_dir(config.source_dir, source_file_path)
            )
            if target_file_path.exists():
                raise FilenameClashError(
                    config.source_dir,
                    Path(str(source_file_path).removesuffix(JINJA_FILENAME_SUFFIX)),
                    source_file_path,
                )
            with open(target_file_path, 'w') as fh:
                fh.write(rendered_file_content)
        else:
            target_file_path = JinjaFileRenderer._calc_target_file_path(config, source_file_path)
            JinjaFileRenderer._logger.debug(
                'Found file "%s", going to copy to: %s',
                source_file_path,
                target_file_path,
            )
            if target_file_path.exists():  # should be unreachable code
                raise FilenameClashError(
                    config.source_dir,
                    target_file_path,
                    Path(str(target_file_path) + JINJA_FILENAME_SUFFIX),
                )
            shutil.copy(source_file_path, target_file_path)

    def copy_and_render_files(self) -> None:
        if self._config.target_dir_content_deletion_mode == TargetDirContentDeletionMode.DO_DELETE:
            self._delete_directory_content(self._config.target_dir)
        if len(os.listdir(self._config.target_dir)) > 0:
            raise TargetDirNotEmptyError(self._config.target_dir)

        renderer: JinjaFileRendererEnvironment = JinjaFileRendererEnvironment(self._config)

        for root, dirs, files in os.walk(self._config.source_dir):
            # start with the files, some have to be rendered, others have to be copied as is.
            for source_file in files:
                JinjaFileRenderer._handle_file(renderer, self._config, root, source_file)
            # create target subdirectory structure for "deeper" files
            for dir_name in dirs:
                source_subdir: Path = Path(root).joinpath(dir_name)
                target_subdir = JinjaFileRenderer._calc_target_subdir(self._config, source_subdir)
                self._logger.debug(
                    'Found directory "%s", going to create directory: %s',
                    source_subdir,
                    target_subdir,
                )
                os.makedirs(target_subdir)
