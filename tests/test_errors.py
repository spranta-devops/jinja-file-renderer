from pathlib import Path

import pytest

from jinja_file_renderer.renderer import FilenameClashError, TargetDirNotEmptyError


class TestErrorConstructors:
    def test_target_dir_not_empty_exception(self) -> None:
        e: TargetDirNotEmptyError = TargetDirNotEmptyError(Path('/tmp/test'))
        assert hasattr(e, 'target_dir')
        assert e.target_dir is not None

    def test_filename_clash_exception(self) -> None:
        e: FilenameClashError = FilenameClashError(
            Path('/tmp/does-not-exist'),
            Path('/tmp/does-not-exist/file.txt'),
            Path('/tmp/does-not-exist/file.txt.jinja'),
        )
        assert hasattr(e, 'source_dir')
        assert hasattr(e, 'template_file')
        assert hasattr(e, 'non_template_file')
        assert e.source_dir is not None
        assert e.source_dir is not None
        assert e.source_dir is not None
        assert str(e) == (
            'The filename of the template file "/tmp/does-not-exist/file.txt" clashes '
            'with the non-template file "/tmp/does-not-exist/file.txt.jinja".'
        )

    def test_invalid_constructor_arg1(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument source_dir[.]',
        ):
            FilenameClashError(
                None,  # type: ignore
                Path('/tmp/does-not-exist/file.txt'),
                Path('/tmp/does-not-exist/file.txt.jinja'),
            )

    def test_invalid_constructor_arg2(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument template_file[.]',
        ):
            FilenameClashError(
                Path('/tmp/does-not-exist'),
                None,  # type: ignore
                Path('/tmp/does-not-exist/file.txt.jinja'),
            )

    def test_invalid_constructor_arg3(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument non_template_file[.]',
        ):
            FilenameClashError(
                Path('/tmp/does-not-exist'),
                Path('/tmp/does-not-exist/file.txt'),
                None,  # type: ignore
            )
