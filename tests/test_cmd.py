import os
import shutil
from unittest.case import TestCase, skip

from click.testing import CliRunner
from tagger import cmd
from tagger.core import AUDIO_FILE_METADATA_FIELDS, EasyFileUtils, MetaDataTagUtils
from tagger.utils import drop_keys

from tagger.tagger_cli import main

json_filename = "tests/resources/backup.json"
mp3_filename = "tests/resources/test.mp3"
mixxxdb_filename = "tests/resources/mixxxdb.sqlite"
resource_dir = "tests/resources/output"

rename_json_filename = "tests/resources/rename.json"
mp3_rename_before_filename = "tests/resources/test_rename.mp3"
mp3_rename_after_filename = "tests/resources/flavour-town.mp3"


def get_mp3_fullname(filename):
    return os.path.join(os.getcwd(), filename)


def reset_tags(audio_filename):
    tags = EasyFileUtils.read_tags_from_existing(audio_filename)
    MetaDataTagUtils.clear_all_specified_metadata(tags, AUDIO_FILE_METADATA_FIELDS)
    MetaDataTagUtils.add_metadata_tags(tags, "xxx", AUDIO_FILE_METADATA_FIELDS)
    EasyFileUtils.write_tags_to_files(tags)
    new_tags = EasyFileUtils.read_tags_from_existing([audio_filename])
    assert new_tags == [
        {
            "filename": "test.mp3",
            "_filename": get_mp3_fullname(mp3_filename),
            "ext": ".mp3",
            "album": "xxx",
            "title": "xxx",
            "artist": "xxx",
            "genre": "xxx",
            "comment": "xxx",
        }
    ]


def nuke_output_dir():
    shutil.rmtree(resource_dir, ignore_errors=True)


def rm_file(filename):
    try:
        os.remove(mp3_rename_before_filename)
    except FileNotFoundError:
        ...


def reset_rename():
    rm_file(mp3_rename_before_filename)
    rm_file(mp3_rename_after_filename)
    shutil.copy(mp3_filename, mp3_rename_before_filename)


# TODO
# - failed and missing files
# - multiple tags

class CmdTests(TestCase):
    def test_restore_metadata_tags_from_backup__is_successful(self):
        """
        FUTURE: include other filetypes beyond mp3.
        """
        reset_tags(
            audio_filename=mp3_filename
        )  # Ensure test audio file is in an expected state

        cmd.restore_metadata_tags_from_backup(json_filename)
        result = EasyFileUtils.read_tags_from_existing([mp3_filename])
        assert drop_keys(result, "_filename") == [
            {
                "filename": "test.mp3",
                "ext": ".mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#genre",
                "comment": "@comment",
            }
        ]

    def test_create_backup__with_mixxx__is_successfull(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = resource_dir
        cmd.create_backup(library_type, mixxxdb_filename, output_directory)
        backup_file = os.listdir(resource_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(resource_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "filename": "test.mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#genre",
                "comment": "@comment",
            }
        ]

    def test_generate_metadata_tags_from_library(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = resource_dir
        cmd.generate_metadata_tags_from_library(
            library_type, mixxxdb_filename, output_directory
        )
        backup_file = os.listdir(resource_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(resource_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "title": "title",
                "artist": "artist",
                "album": "album",
                "genre": "",
                "comment": "",
                "filename": "test.mp3",
            }
        ]

    def test_rename_files(self):
        reset_rename()
        cmd.apply_renaming_to_files(rename_json_filename)
        results = EasyFileUtils.read_tags_from_existing(mp3_rename_after_filename)
        assert results == [
            {
                "filename": "flavour-town.mp3",
                "_filename": get_mp3_fullname(mp3_rename_after_filename),
                "ext": ".mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#genre",
                "comment": "@comment",
            }
        ]


class ClickCliTests(TestCase):
    def test_help(self):
        runner = CliRunner()
        results = runner.invoke(main, ["--help"])
        assert results.exit_code == 0

    def test_restore__is_successful(self):
        """
        FUTURE: include other filetypes beyond mp3.
        """
        reset_tags(
            audio_filename=mp3_filename
        )  # Ensure test audio file is in an expected state

        runner = CliRunner()
        results = runner.invoke(main, ["apply", "--json-file", json_filename])
        assert results.exit_code == 0

        result = EasyFileUtils.read_tags_from_existing([mp3_filename])
        assert drop_keys(result, "_filename") == [
            {
                "filename": "test.mp3",
                "ext": ".mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#genre",
                "comment": "@comment",
            }
        ]

    def test__backup__is_successfull(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = resource_dir

        runner = CliRunner()
        results = runner.invoke(
            main,
            [
                "backup",
                "--type",
                library_type,
                "--libpath",
                mixxxdb_filename,
                "--output-dir",
                output_directory,
            ],
        )
        assert results.exit_code == 0

        backup_file = os.listdir(resource_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(resource_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "filename": "test.mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#genre",
                "comment": "@comment",
            }
        ]

    def test_make_tags__is_successful(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = resource_dir

        runner = CliRunner()
        results = runner.invoke(
            main,
            [
                "make-tags",
                "--type",
                library_type,
                "--libpath",
                mixxxdb_filename,
                "--output-dir",
                output_directory,
            ],
        )
        assert results.exit_code == 0

        backup_file = os.listdir(resource_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(resource_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "title": "title",
                "artist": "artist",
                "album": "album",
                "genre": "",
                "comment": "",
                "filename": "test.mp3",
            }
        ]

    def test_rename_files(self):
        reset_rename()

        runner = CliRunner()
        results = runner.invoke(main, ["rename", "--json-file", rename_json_filename])
        assert results.exit_code == 0

        results = EasyFileUtils.read_tags_from_existing(mp3_rename_after_filename)
        assert results == [
            {
                "filename": "flavour-town.mp3",
                "_filename": get_mp3_fullname(mp3_rename_after_filename),
                "ext": ".mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#genre",
                "comment": "@comment",
            }
        ]

    ...
