import os
from argparse import ArgumentTypeError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from jinja_file_renderer import cli


class TestArgparseWriteableDir:
    def test_with_tmp_path(self, tmp_path) -> None:
        parsed_path: Path = cli._argparse_writeable_dir(str(tmp_path))
        assert parsed_path == tmp_path

    def test_not_exists(self) -> None:
        with pytest.raises(
            ArgumentTypeError, match='writeable_dir: "this-directory-should-not-exist" does not exists.'
        ):
            cli._argparse_writeable_dir('this-directory-should-not-exist')

    def test_is_no_dir(self, tmp_path) -> None:
        filepath: Path = tmp_path.joinpath('testfile.txt')
        with open(filepath, mode='w'):
            pass
        with pytest.raises(ArgumentTypeError, match='writeable_dir: ".*/testfile[.]txt" is not a directory[.]'):
            cli._argparse_writeable_dir(str(filepath))

    def test_not_writeable(self, tmp_path) -> None:
        readonly_dir: Path = tmp_path.joinpath('readonly-dir')
        os.mkdir(readonly_dir, mode=0o400)
        with pytest.raises(ArgumentTypeError, match='writeable_dir: ".*readonly-dir" is not writeable.'):
            cli._argparse_writeable_dir(str(readonly_dir))
