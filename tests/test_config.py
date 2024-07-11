import os
import re
from pathlib import Path

import pytest

from jinja_file_renderer import cli
from jinja_file_renderer.config import (
    DEFAULT_DOTENV_FILES,
    RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON,
    JinjaFileRendererConfig,
    TargetDirContentDeletionMode,
)


class TestJinjaFileRendererConfig:
    def test_noargs(self) -> None:
        with pytest.raises(SystemExit):
            cli._parse_arguments([])

    def test_to_string(self) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        str_value: str = config.to_string()
        assert re.match(
            r'JinjaFileRendererConfig\['
            r'\n {2}source_dir=sourceDir'
            r'\n {2}target_dir=targetDir'
            r'\n {2}dotenv_files=\[PosixPath\(\'os.env\'\), PosixPath\(\'.env\'\)]'
            r'\n {2}target_dir_content_deletion_mode=TargetDirContentDeletionMode.DO_NOT_DELETE'
            r'\n]',
            str_value,
        )

    def test_no_templating_vars(self) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path](),
        )
        assert len(config.template_vars) == 0

    def test_collect_os_environ_vars(self, monkeypatch) -> None:
        monkeypatch.setenv('PYTEST_KEY1', 'PYTEST_VALUE1')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON]),
        )
        assert os.environ.get('PYTEST_KEY1') == 'PYTEST_VALUE1'
        assert config.template_vars.get('PYTEST_KEY1') == 'PYTEST_VALUE1'

    def test_collect_dotenv_environ_vars(self, tmp_path) -> None:
        test_dotenv_file: Path = tmp_path.joinpath('test.dotenv')
        with open(test_dotenv_file, mode='w') as text_file:
            text_file.write('PYTEST_KEY1=PYTEST_VALUE1')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([test_dotenv_file]),
        )
        assert config.template_vars.get('PYTEST_KEY1') == 'PYTEST_VALUE1'

    def test_collect_dotenv_environ_vars_illegal_arg1(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument collected[.]',
        ):
            JinjaFileRendererConfig._collect_dotenv_vars(None, Path('.env'))  # type: ignore

    def test_collect_dotenv_environ_vars_illegal_arg2(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument dotenv_file[.]',
        ):
            JinjaFileRendererConfig._collect_dotenv_vars({}, None)  # type: ignore

    def test_collect_os_environ_vars_illegal_arg(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument collected[.]',
        ):
            JinjaFileRendererConfig._collect_os_environ_vars(None)  # type: ignore

    def test_collect_empty_dotenv_file(self, tmp_path) -> None:
        empty_dotenv_file: Path = tmp_path.joinpath('empty.dotenv')
        with open(empty_dotenv_file, mode='w'):
            pass
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([empty_dotenv_file]),
        )
        assert config.template_vars == dict[str, str]()

    def test_dotenv_var_overwrites_os_env_var(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv('PYTEST_KEY1', 'OS-ENV-VALUE')
        test_dotenv_file: Path = tmp_path.joinpath('test.dotenv')
        with open(test_dotenv_file, mode='w') as text_file:
            text_file.write('PYTEST_KEY1=DOTENV-VALUE')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([Path('os.env'), test_dotenv_file]),
        )
        assert config.template_vars.get('PYTEST_KEY1') == 'DOTENV-VALUE'

    def test_os_env_var_overwrites_dotenv_var(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv('PYTEST_KEY1', 'OS-ENV-VALUE')
        test_dotenv_file: Path = tmp_path.joinpath('test.dotenv')
        with open(test_dotenv_file, mode='w') as text_file:
            text_file.write('PYTEST_KEY1=DOTENV-VALUE')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([test_dotenv_file, Path('os.env')]),
        )
        assert config.template_vars.get('PYTEST_KEY1') == 'OS-ENV-VALUE'

    def test_os_env_var_without_value(self, monkeypatch) -> None:
        monkeypatch.setenv('PYTEST_KEY1', '')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([Path('os.env')]),
        )
        assert config.template_vars.get('PYTEST_KEY1') == ''
        assert config.template_vars.get('NON-EXISTING-KEY') is None

    def test_dotenv_var_without_value(self, tmp_path) -> None:
        test_dotenv_file: Path = tmp_path.joinpath('test.dotenv')
        with open(test_dotenv_file, mode='w') as text_file:
            text_file.write('PYTEST_KEY1=')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('sourceDir'),
            Path('targetDir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([test_dotenv_file]),
        )
        assert config.template_vars.get('PYTEST_KEY1') == ''
        assert config.template_vars.get('NON-EXISTING-KEY') is None

    def test_constructor_illegal_arg1(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument source_dir[.]',
        ):
            JinjaFileRendererConfig(
                None,  # type: ignore
                Path('target-dir'),
                TargetDirContentDeletionMode.DO_NOT_DELETE,
                DEFAULT_DOTENV_FILES,
            )

    def test_constructor_illegal_arg2(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument target_dir[.]',
        ):
            JinjaFileRendererConfig(
                Path('source-dir'),
                None,  # type: ignore
                TargetDirContentDeletionMode.DO_NOT_DELETE,
                DEFAULT_DOTENV_FILES,
            )

    def test_constructor_illegal_arg3(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument target_dir_content_deletion_mode[.]',
        ):
            JinjaFileRendererConfig(
                Path('source-dir'),
                Path('target-dir'),
                None,  # type: ignore
                DEFAULT_DOTENV_FILES,
            )

    def test_constructor_illegal_arg4(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument dotenv_files[.]',
        ):
            JinjaFileRendererConfig(
                Path('source-dir'),
                Path('target-dir'),
                TargetDirContentDeletionMode.DO_NOT_DELETE,
                None,  # type: ignore
            )
