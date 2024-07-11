# SPDX-FileCopyrightText: 2024 Gerd Aschbrenner
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import re
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.capture import CaptureResult

from jinja_file_renderer import cli


class TestCli:

    def test_main(self, capsys: pytest.CaptureFixture) -> None:
        cli.main()
        captured: CaptureResult = capsys.readouterr()
        assert captured.out == ''
        assert captured.err == ''

    def test_cli_no_arg(self, capsys: pytest.CaptureFixture) -> None:
        cli.cli(list[str]())
        captured: CaptureResult = capsys.readouterr()
        assert captured.out == ''
        assert captured.err == ''
