import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.capture import CaptureResult

from jinja_file_renderer import cli
from jinja_file_renderer.__about__ import __version__


class TestCli:
    @pytest.fixture
    def source_dirs(self, request) -> Path:
        filename = request.module.__file__
        test_dir = os.path.dirname(filename)
        return Path(test_dir).joinpath('source-dirs')

    def test_no_arg(self, capsys: pytest.CaptureFixture) -> None:
        with pytest.raises(SystemExit) as se:
            cli.main(list[str]([]))
        assert se.type is SystemExit
        assert se.value.code == 2
        captured: CaptureResult = capsys.readouterr()
        assert captured.out == ''
        assert re.match(
            r'usage: jinja-file-renderer\s+\[-h]\s+\[--version]\s+\[--log-level LOG-LEVEL]'
            r'\s+\[--dotenv-files \[FILE ...]]\s+\[--delete-target-dir-content]'
            r'\s+--source-dir\s+DIRECTORY\s+--target-dir\s+DIRECTORY'
            r'\s+jinja-file-renderer: error: the following arguments are required: --source-dir, --target-dir',
            captured.err,
        )

    def test_version(self, capsys: pytest.CaptureFixture) -> None:
        with pytest.raises(SystemExit) as se:
            cli.main(list[str](['--version']))
        assert se.type is SystemExit
        assert se.value.code == 0
        captured: CaptureResult = capsys.readouterr()
        assert captured.out == f'jinja-file-renderer ({__version__})\n'
        assert captured.err == ''

    def test_help(self, capsys: pytest.CaptureFixture) -> None:
        with pytest.raises(SystemExit) as se:
            cli.main(list[str](['--help']))
        assert se.type is SystemExit
        assert se.value.code == 0
        captured: CaptureResult = capsys.readouterr()
        assert captured.out.startswith('usage: jinja-file-renderer')
        assert captured.err == ''

    def test_with_yaml_files(self, tmp_path: Path, capsys: pytest.CaptureFixture, source_dirs: Path) -> None:
        source_dir: Path = source_dirs.joinpath('yaml-files')
        target_dir = tmp_path.joinpath('target-dir')
        os.mkdir(target_dir)

        cli.main(list[str](['--source-dir', str(source_dir), '--target-dir', str(target_dir)]))
        captured: CaptureResult = capsys.readouterr()
        assert captured.out == ''
        assert captured.err == ''

    def test_filename_clash(self, tmp_path: Path, capsys: pytest.CaptureFixture, source_dirs: Path) -> None:
        source_dir: Path = source_dirs.joinpath('filename-clash')
        target_dir = tmp_path.joinpath('target-dir')
        os.mkdir(target_dir)

        with pytest.raises(SystemExit) as se:
            cli.main(list[str](['--source-dir', str(source_dir), '--target-dir', str(target_dir)]))
        assert se.type is SystemExit
        assert se.value.code == 1
        captured: CaptureResult = capsys.readouterr()
        assert captured.out == ''
        assert re.match(
            r'The filename of the template file ".*/tests/source-dirs/filename-clash/same-filename.txt" clashes '
            r'with the non-template file ".*/tests/source-dirs/filename-clash/same-filename.txt.jinja"[.]',
            captured.err,
        )
