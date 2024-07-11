import os
import re
from pathlib import Path

import pytest

from jinja_file_renderer.config import (
    RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON,
    JinjaFileRendererConfig,
    TargetDirContentDeletionMode,
)
from jinja_file_renderer.renderer import JinjaFileRendererEnvironment, TemplateVariableUndefinedError


class TestJinjaFileRendererEnvironment:
    @pytest.fixture
    def source_dirs(self, request) -> Path:
        filename = request.module.__file__
        test_dir = os.path.dirname(filename)
        return Path(test_dir).joinpath('source-dirs')

    def test_missing_template_var(self, source_dirs) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('sample-files'),
            Path('target-dir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON]),
        )
        jfr_env: JinjaFileRendererEnvironment = JinjaFileRendererEnvironment(config)
        with pytest.raises(
            TemplateVariableUndefinedError,
            match=r'The template_file "hello-username[.]txt" uses the undefined variable "PYTEST_USERNAME"[.]',
        ):
            jfr_env.render(Path('hello-username.txt'))

    def test_empty_template_var(self, monkeypatch, source_dirs) -> None:
        monkeypatch.setenv('PYTEST_USERNAME', '')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('sample-files'),
            Path('target-dir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON]),
        )
        jfr_env: JinjaFileRendererEnvironment = JinjaFileRendererEnvironment(config)
        result: str = jfr_env.render(Path('hello-username.txt'))
        assert result == 'Hello !\n'

    def test_hello_username(self, monkeypatch, source_dirs) -> None:
        monkeypatch.setenv('PYTEST_USERNAME', 'pytest')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('sample-files'),
            Path('target-dir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON]),
        )
        jfr_env: JinjaFileRendererEnvironment = JinjaFileRendererEnvironment(config)
        result: str = jfr_env.render(Path('hello-username.txt'))
        assert re.match(r'Hello pytest!\n', result)

    def test_invalid_constructor_none(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument config[.]',
        ):
            JinjaFileRendererEnvironment(None)  # type: ignore
