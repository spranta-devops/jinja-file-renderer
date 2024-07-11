import filecmp
import os
import shutil
from pathlib import Path

import pytest

from jinja_file_renderer.config import (
    DEFAULT_DOTENV_FILES,
    RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON,
    JinjaFileRendererConfig,
    TargetDirContentDeletionMode,
)
from jinja_file_renderer.renderer import (
    JINJA_FILENAME_SUFFIX,
    FilenameClashError,
    JinjaFileRenderer,
    TargetDirNotEmptyError,
    TemplateVariableUndefinedError,
)


class TestJinjaFileRenderer:
    @pytest.fixture
    def source_dirs(self, request) -> Path:
        filename = request.module.__file__
        test_dir = os.path.dirname(filename)
        return Path(test_dir).joinpath('source-dirs')

    @pytest.fixture
    def target_dir(self, tmp_path) -> Path:
        target_dir = tmp_path.joinpath('target-dir')
        os.mkdir(target_dir)
        return target_dir

    @staticmethod
    def _assert_calc_target_subdir(source_dir: Path, target_dir: Path):
        assert source_dir is not None
        assert target_dir is not None
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dir,
            target_dir,
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )

        txt_testfile: Path = source_dir.joinpath('testfile.txt')
        txt_result: Path = JinjaFileRenderer._calc_target_subdir(config, txt_testfile)
        assert txt_result == target_dir.joinpath('testfile.txt')

        subdir_testfile: Path = source_dir.joinpath('dir1').joinpath('testfile.txt')
        subdir_result: Path = JinjaFileRenderer._calc_target_subdir(config, subdir_testfile)
        assert subdir_result == target_dir.joinpath('dir1').joinpath('testfile.txt')

        sub_subdir_testfile: Path = source_dir.joinpath('dir1').joinpath('dir2').joinpath('testfile.txt')
        sub_subdir_result: Path = JinjaFileRenderer._calc_target_subdir(config, sub_subdir_testfile)
        assert sub_subdir_result == target_dir.joinpath('dir1').joinpath('dir2').joinpath('testfile.txt')

    def test_calc_target_subdir_with_relative_path(self) -> None:
        source_dir: Path = Path('source-dir')
        target_dir: Path = Path('target-dir')
        TestJinjaFileRenderer._assert_calc_target_subdir(source_dir, target_dir)

    def test_calc_target_subdir_with_absolute_path(self) -> None:
        source_dir: Path = Path('/tmp/source-dir')
        target_dir: Path = Path('/tmp/target-dir')
        TestJinjaFileRenderer._assert_calc_target_subdir(source_dir, target_dir)

    def test_calc_target_subdir_with_different_root(self) -> None:
        source_dir: Path = Path('/a/b/c/d/source-dir')
        target_dir: Path = Path('target-dir')
        TestJinjaFileRenderer._assert_calc_target_subdir(source_dir, target_dir)

    def test_calc_target_subdir_illegal_arg1(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument config[.]',
        ):
            JinjaFileRenderer._calc_target_subdir(None, Path('testfile.txt'))  # type: ignore

    def test_calc_target_subdir_illegal_arg2(self) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('source-dir'),
            Path('target-dir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument source_subdir[.]',
        ):
            JinjaFileRenderer._calc_target_subdir(config, None)  # type: ignore

    def test_calc_target_file_path(self) -> None:
        source_dir: Path = Path('source-dir')
        target_dir: Path = Path('target-dir')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dir,
            target_dir,
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        testfile = source_dir.joinpath('testfile.txt.jinja')
        assert JinjaFileRenderer._calc_target_file_path(config, testfile) == target_dir.joinpath('testfile.txt')

        testfile = source_dir.joinpath('testfile.txt')
        assert JinjaFileRenderer._calc_target_file_path(config, testfile) == target_dir.joinpath('testfile.txt')

    def test_calc_target_file_path_with_too_short_filename(self) -> None:
        source_dir: Path = Path('source-dir')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dir,
            Path('target-dir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        testfile = source_dir.joinpath(JINJA_FILENAME_SUFFIX)
        with pytest.raises(
            ValueError,
            match=r'The source_filename \(source-dir/[.]jinja\) would be empty after removing the "[.]jinja" suffix[.]',
        ):
            JinjaFileRenderer._calc_target_file_path(config, testfile)

    def test_calc_target_file_path_illegal_arg1(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument config[.]',
        ):
            JinjaFileRenderer._calc_target_file_path(None, Path('testfile.txt'))  # type: ignore

    def test_calc_target_file_path_illegal_arg2(self) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            Path('source-dir'),
            Path('target-dir'),
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument source_file[.]',
        ):
            JinjaFileRenderer._calc_target_file_path(config, None)  # type: ignore

    def test_calc_source_file_path_without_source_dir(self) -> None:
        source_dir: Path = Path('source-dir')
        file: Path = Path('test_file.txt')
        source_file: Path = Path(source_dir.joinpath(file))
        sanitized_file: Path = JinjaFileRenderer._calc_source_file_path_without_source_dir(source_dir, source_file)
        assert sanitized_file == file

    def test_calc_source_file_path_without_source_dir_illegal_arg1(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument source_dir[.]',
        ):
            JinjaFileRenderer._calc_source_file_path_without_source_dir(None, Path('file.txt'))  # type: ignore

    def test_calc_source_file_path_without_source_dir_illegal_arg2(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument source_file_path[.]',
        ):
            JinjaFileRenderer._calc_source_file_path_without_source_dir(Path('source-dir'), None)  # type: ignore

    def test_calc_source_file_path_without_source_dir_switched_args(self) -> None:
        source_dir: Path = Path('source-dir')
        source_file: Path = Path(source_dir.joinpath('test_file.txt'))
        with pytest.raises(
            ValueError,
            match=(
                r'Expected value of source_file_path \(source-dir\) is longer than source_dir '
                r'\(source-dir/test_file.txt\)[.]'
            ),
        ):
            JinjaFileRenderer._calc_source_file_path_without_source_dir(source_file, source_dir)

    def test_delete_directory_content(self, tmp_path: Path, source_dirs: Path) -> None:
        test_path: Path = tmp_path.joinpath('test-dir')
        shutil.copytree(source_dirs.joinpath('yaml-files'), test_path)
        assert sum([len(files) for _, _, files in os.walk(test_path)]) == 14
        assert sum([len(directories) for _, directories, _ in os.walk(test_path)]) == 6
        JinjaFileRenderer._delete_directory_content(test_path)
        assert test_path.exists()
        assert test_path.is_dir()
        assert sum([len(files) for _, _, files in os.walk(test_path)]) == 0
        assert sum([len(directories) for _, directories, _ in os.walk(test_path)]) == 0

    def test_delete_directory_content_invalid_arg(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument directory[.]',
        ):
            JinjaFileRenderer._delete_directory_content(None)  # type: ignore

    def test_delete_directory_content_directory_does_not_exist(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'The directory /does-not-exist does not exist[.]',
        ):
            JinjaFileRenderer._delete_directory_content(Path('/does-not-exist'))

    def test_delete_directory_content_directory_is_not_a_dir(self, tmp_path: Path) -> None:
        file: Path = tmp_path.joinpath('testfile.txt')
        with open(file, mode='w'):
            pass
        with pytest.raises(
            ValueError,
            match=r'The directory .*/testfile.txt is not a directory[.]',
        ):
            JinjaFileRenderer._delete_directory_content(file)

    def test_filename_clash(self, source_dirs: Path, target_dir: Path) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('filename-clash'),
            target_dir,
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        jfr: JinjaFileRenderer = JinjaFileRenderer(config)
        with pytest.raises(FilenameClashError):
            jfr.copy_and_render_files()

    def test_target_dir_not_empty(self, source_dirs: Path, target_dir: Path) -> None:
        with open(target_dir.joinpath('dir-not-empty-file.txt'), mode='w'):
            pass
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('yaml-files'),
            target_dir,
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        jfr: JinjaFileRenderer = JinjaFileRenderer(config)
        with pytest.raises(TargetDirNotEmptyError):
            jfr.copy_and_render_files()

    def test_with_target_dir_content_deletion(self, source_dirs: Path, target_dir: Path) -> None:
        with open(target_dir.joinpath('dir-not-empty-file.txt'), mode='w'):
            pass
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('yaml-files'),
            target_dir,
            TargetDirContentDeletionMode.DO_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        jfr: JinjaFileRenderer = JinjaFileRenderer(config)
        jfr.copy_and_render_files()

    def test_with_target_dir_content_deletion_but_already_empty(self, source_dirs: Path, target_dir: Path) -> None:
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('yaml-files'),
            target_dir,
            TargetDirContentDeletionMode.DO_DELETE,
            DEFAULT_DOTENV_FILES,
        )
        jfr: JinjaFileRenderer = JinjaFileRenderer(config)
        jfr.copy_and_render_files()

    def test_missing_template_var(self, monkeypatch, source_dirs: Path, target_dir: Path) -> None:
        monkeypatch.delenv('USER')
        monkeypatch.delenv('LANG')
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('yaml-files'),
            target_dir,
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON]),
        )
        renderer: JinjaFileRenderer = JinjaFileRenderer(config)
        with pytest.raises(
            TemplateVariableUndefinedError,
            match=r'The template_file "configmap[.]yaml[.]jinja" uses the undefined variable "USER"[.]',
        ):
            renderer.copy_and_render_files()

    def test_target_dir_output(self, monkeypatch, source_dirs: Path, target_dir: Path) -> None:
        monkeypatch.setenv('USER', 'pytest')
        monkeypatch.setenv('LANG', 'eo_XX.UTF-8')  # Esperanto
        config: JinjaFileRendererConfig = JinjaFileRendererConfig(
            source_dirs.joinpath('yaml-files'),
            target_dir,
            TargetDirContentDeletionMode.DO_NOT_DELETE,
            list[Path]([RESERVED_DOTENV_FILENAME_FOR_OS_ENVIRON]),
        )
        jfr: JinjaFileRenderer = JinjaFileRenderer(config)
        jfr.copy_and_render_files()

        rendered_root_configmap: Path = target_dir.joinpath('configmap.yaml')
        assert rendered_root_configmap.exists()
        assert rendered_root_configmap.is_file()
        with open(rendered_root_configmap) as file:
            file_content = file.read()
        assert file_content == (
            '---\n'
            'apiVersion: v1\n'
            'kind: ConfigMap\n'
            'metadata:\n'
            "  name: 'jinja-file-renderer'\n"
            "  namespace: 'jinja-file-renderer'\n"
            'data:\n'
            "  USER: 'pytest'\n"
            "  LANG: 'eo_XX.UTF-8'\n"
        )

        rendered_subdir1_configmap: Path = target_dir.joinpath('subdir1').joinpath('subdir1-configmap.yaml')
        assert rendered_root_configmap.exists()
        assert rendered_root_configmap.is_file()

        rendered_subdir11_configmap: Path = (
            target_dir.joinpath('subdir1').joinpath('subdir11').joinpath('subdir11-configmap.yaml')
        )
        assert rendered_subdir11_configmap.exists()
        assert rendered_subdir11_configmap.is_file()

        rendered_subdir12_configmap: Path = (
            target_dir.joinpath('subdir1').joinpath('subdir12').joinpath('subdir12-configmap.yaml')
        )
        assert rendered_subdir12_configmap.exists()
        assert rendered_subdir12_configmap.is_file()

        rendered_subdir2_configmap: Path = target_dir.joinpath('subdir2').joinpath('subdir2-configmap.yaml')
        assert rendered_root_configmap.exists()
        assert rendered_root_configmap.is_file()

        rendered_subdir21_configmap: Path = (
            target_dir.joinpath('subdir2').joinpath('subdir21').joinpath('subdir21-configmap.yaml')
        )
        assert rendered_subdir21_configmap.exists()
        assert rendered_subdir21_configmap.is_file()

        rendered_subdir22_configmap: Path = (
            target_dir.joinpath('subdir2').joinpath('subdir22').joinpath('subdir22-configmap.yaml')
        )
        assert rendered_subdir22_configmap.exists()
        assert rendered_subdir22_configmap.is_file()

        assert filecmp.cmp(rendered_root_configmap, rendered_subdir1_configmap)
        assert filecmp.cmp(rendered_root_configmap, rendered_subdir2_configmap)
        assert filecmp.cmp(rendered_root_configmap, rendered_subdir11_configmap)
        assert filecmp.cmp(rendered_root_configmap, rendered_subdir12_configmap)
        assert filecmp.cmp(rendered_root_configmap, rendered_subdir21_configmap)
        assert filecmp.cmp(rendered_root_configmap, rendered_subdir22_configmap)

        non_template_root_configmap: Path = target_dir.joinpath('non-template-configmap.yaml')
        assert non_template_root_configmap.exists()
        assert non_template_root_configmap.is_file()

        with open(non_template_root_configmap) as file:
            file_content = file.read()
        assert file_content == (
            '---\n'
            'apiVersion: v1\n'
            'kind: ConfigMap\n'
            'metadata:\n'
            "  name: 'jinja-file-renderer'\n"
            "  namespace: 'jinja-file-renderer'\n"
            'data:\n'
            "  key: 'value'\n"
            "  USER: '{{ USER }}'  # should not be rendered\n"
            "  LANG: '{{ LANG }}'  # should not be rendered\n"
        )

        non_template_subdir1_configmap: Path = target_dir.joinpath('subdir1').joinpath(
            'subdir1-non-template-configmap.yaml'
        )
        assert non_template_subdir1_configmap.exists()
        assert non_template_subdir1_configmap.is_file()

        non_template_subdir2_configmap: Path = target_dir.joinpath('subdir2').joinpath(
            'subdir2-non-template-configmap.yaml'
        )
        assert non_template_subdir2_configmap.exists()
        assert non_template_subdir2_configmap.is_file()

        non_template_subdir11_configmap: Path = (
            target_dir.joinpath('subdir1').joinpath('subdir11').joinpath('subdir11-non-template-configmap.yaml')
        )
        assert non_template_subdir11_configmap.exists()
        assert non_template_subdir11_configmap.is_file()

        non_template_subdir12_configmap: Path = (
            target_dir.joinpath('subdir1').joinpath('subdir12').joinpath('subdir12-non-template-configmap.yaml')
        )
        assert non_template_subdir12_configmap.exists()
        assert non_template_subdir12_configmap.is_file()

        non_template_subdir21_configmap: Path = (
            target_dir.joinpath('subdir2').joinpath('subdir21').joinpath('subdir21-non-template-configmap.yaml')
        )
        assert non_template_subdir21_configmap.exists()
        assert non_template_subdir21_configmap.is_file()

        non_template_subdir22_configmap: Path = (
            target_dir.joinpath('subdir2').joinpath('subdir22').joinpath('subdir22-non-template-configmap.yaml')
        )
        assert non_template_subdir22_configmap.exists()
        assert non_template_subdir22_configmap.is_file()

        assert filecmp.cmp(non_template_root_configmap, non_template_subdir1_configmap)
        assert filecmp.cmp(non_template_root_configmap, non_template_subdir2_configmap)
        assert filecmp.cmp(non_template_root_configmap, non_template_subdir11_configmap)
        assert filecmp.cmp(non_template_root_configmap, non_template_subdir12_configmap)
        assert filecmp.cmp(non_template_root_configmap, non_template_subdir21_configmap)
        assert filecmp.cmp(non_template_root_configmap, non_template_subdir22_configmap)

    def test_invalid_constructor(self) -> None:
        with pytest.raises(
            ValueError,
            match=r'Expected a value for the argument config[.]',
        ):
            JinjaFileRenderer(None)  # type: ignore
