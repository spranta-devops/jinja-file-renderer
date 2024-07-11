import os
from argparse import ArgumentTypeError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from jinja_file_renderer import cli


class TestArgparseReadableDir:
    def test_with_tmp_path(self, tmp_path) -> None:
        parsed_path: Path = cli._argparse_readable_dir(str(tmp_path))
        assert parsed_path == tmp_path

    def test_not_exists(self) -> None:
        with pytest.raises(ArgumentTypeError, match='readable_dir: "this-directory-should-not-exist" does not exists.'):
            cli._argparse_readable_dir('this-directory-should-not-exist')

    def test_is_no_dir(self, tmp_path) -> None:
        filepath = tmp_path.joinpath('testfile.txt')
        with open(filepath, mode='w'):
            pass
        with pytest.raises(ArgumentTypeError, match='readable_dir: ".*/testfile[.]txt" is not a directory[.]'):
            cli._argparse_readable_dir(str(filepath))

    def test_dir_not_readable(self, tmp_path) -> None:
        not_readable_dir = tmp_path.joinpath('not-readable-dir')
        try:
            os.mkdir(not_readable_dir, mode=0o100)
            with pytest.raises(ArgumentTypeError, match='readable_dir: ".*/not-readable-dir" is not readable[.]'):
                cli._argparse_readable_dir(str(not_readable_dir))
        finally:
            # pytest can not clean up the temp directory when it is not readable
            not_readable_dir.chmod(mode=0o400)
