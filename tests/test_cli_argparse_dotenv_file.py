import os
from argparse import ArgumentTypeError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from jinja_file_renderer import cli


class TestArgparseDotenvFiles:
    def test_with_existing_file(self, tmp_path) -> None:
        existing_filepath = tmp_path.joinpath('empty-existing.env')
        with open(existing_filepath, mode='w'):
            pass
        result: Path = cli._argparse_dotenv_file(str(existing_filepath))
        assert result == existing_filepath

    def test_with_nonexisting_file(self, tmp_path) -> None:
        non_existing_filepath = tmp_path.joinpath('non-existing.env')
        result: Path = cli._argparse_dotenv_file(str(non_existing_filepath))
        assert result == non_existing_filepath

    def test_is_no_file(self, tmp_path) -> None:
        a_dir_not_a_file: Path = tmp_path.joinpath('a_dir_not_a_file')
        os.mkdir(a_dir_not_a_file, mode=0o400)
        with pytest.raises(ArgumentTypeError, match='dotenv_files: ".*/a_dir_not_a_file" is not a file[.]'):
            cli._argparse_dotenv_file(str(a_dir_not_a_file))

    def test_file_not_readable(self, tmp_path) -> None:
        non_readable_file = tmp_path.joinpath('non-readable-file.txt')
        with open(non_readable_file, mode='w'):
            pass
        try:
            non_readable_file.chmod(mode=0o200)
            with pytest.raises(ArgumentTypeError, match='dotenv_files: ".*/non-readable-file.txt" is not readable[.]'):
                cli._argparse_dotenv_file(str(non_readable_file))
        finally:
            # pytest can not clean up the temp directory when the content is not readable
            non_readable_file.chmod(mode=0o400)
