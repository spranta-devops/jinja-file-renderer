import os
from pathlib import Path

import pytest

from jinja_file_renderer import cli
from jinja_file_renderer.config import (
    DEFAULT_DOTENV_FILES,
    JinjaFileRendererConfig,
    TargetDirContentDeletionMode,
)


class SourceAndTargetDir:
    source_dir: Path
    target_dir: Path

    def __init__(self, source_dir: Path, target_dir: Path):
        assert source_dir is not None
        assert target_dir is not None
        self.source_dir = source_dir
        self.target_dir = target_dir


class TestParseArguments:
    def test_noargs(self) -> None:
        with pytest.raises(SystemExit):
            cli._parse_arguments([])

    @pytest.fixture
    def workdir(self, tmp_path) -> SourceAndTargetDir:
        source_dir: Path = tmp_path.joinpath('source')
        os.mkdir(source_dir, mode=0o700)
        target_dir: Path = tmp_path.joinpath('target')
        os.mkdir(target_dir, mode=0o700)
        return SourceAndTargetDir(source_dir, target_dir)

    def test_default_config(self, workdir: SourceAndTargetDir) -> None:
        assert workdir is not None
        config: JinjaFileRendererConfig = cli._parse_arguments(
            [
                '--source-dir',
                str(workdir.source_dir),
                '--target-dir',
                str(workdir.target_dir),
            ]
        )
        assert config is not None
        assert config.source_dir.resolve() == workdir.source_dir.resolve()
        assert config.target_dir.resolve() == workdir.target_dir.resolve()
        assert config.dotenv_files == DEFAULT_DOTENV_FILES
        assert config.target_dir_content_deletion_mode == TargetDirContentDeletionMode.DO_NOT_DELETE

    def test_with_delete_target_dir_content(self, workdir: SourceAndTargetDir) -> None:
        assert workdir is not None
        config: JinjaFileRendererConfig = cli._parse_arguments(
            [
                '--source-dir',
                str(workdir.source_dir),
                '--target-dir',
                str(workdir.target_dir),
                '--delete-target-dir-content',
            ]
        )
        assert config is not None
        assert config.source_dir.resolve() == workdir.source_dir.resolve()
        assert config.target_dir.resolve() == workdir.target_dir.resolve()
        assert config.dotenv_files == DEFAULT_DOTENV_FILES
        assert config.target_dir_content_deletion_mode == TargetDirContentDeletionMode.DO_DELETE
