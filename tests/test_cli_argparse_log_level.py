import logging
from argparse import ArgumentTypeError

import pytest

from jinja_file_renderer import cli


class TestArgparseLogLevel:
    def test_debug_minuscule(self) -> None:
        log_level: int = cli._argparse_log_level('debug')
        assert log_level == logging.DEBUG

    def test_debug_majuscule(self) -> None:
        log_level: int = cli._argparse_log_level('DEBUG')
        assert log_level == logging.DEBUG

    def test_info_minuscule(self) -> None:
        log_level: int = cli._argparse_log_level('info')
        assert log_level == logging.INFO

    def test_info_majuscule(self) -> None:
        log_level: int = cli._argparse_log_level('INFO')
        assert log_level == logging.INFO

    def test_warning_minuscule(self) -> None:
        log_level: int = cli._argparse_log_level('warning')
        assert log_level == logging.WARNING

    def test_warning_majuscule(self) -> None:
        log_level: int = cli._argparse_log_level('WARNING')
        assert log_level == logging.WARNING

    def test_error_minuscule(self) -> None:
        log_level: int = cli._argparse_log_level('error')
        assert log_level == logging.ERROR

    def test_error_majuscule(self) -> None:
        log_level: int = cli._argparse_log_level('ERROR')
        assert log_level == logging.ERROR

    def test_critical_minuscule(self) -> None:
        log_level: int = cli._argparse_log_level('critical')
        assert log_level == logging.CRITICAL

    def test_critical_majuscule(self) -> None:
        log_level: int = cli._argparse_log_level('CRITICAL')
        assert log_level == logging.CRITICAL

    def test_fatal_minuscule(self) -> None:
        log_level: int = cli._argparse_log_level('fatal')
        assert log_level == logging.CRITICAL

    def test_fatal_majuscule(self) -> None:
        log_level: int = cli._argparse_log_level('FATAL')
        assert log_level == logging.CRITICAL

    def test_invalid(self) -> None:
        with pytest.raises(
            ArgumentTypeError,
            match='log_level: "invalid" is not valid[.]',
        ):
            cli._argparse_log_level('invalid')
