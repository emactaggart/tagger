import os
import shutil
from unittest.case import TestCase, skip

from click.testing import CliRunner
from tagger import cmd
from tagger.core import AUDIO_FILE_METADATA_FIELDS, EasyFileUtils, MetaDataTagUtils
from tagger.utils import absolute_path, drop_keys

from tagger.tagger_cli import main


resource_dir = os.path.join("tests", "resources")
output_dir = os.path.join(resource_dir, "output")

def resource(filename):
    return absolute_path(os.path.join(resource_dir, filename))

json_backup_filename = resource("backup-tags-2021-09-23T11-01.json")
mp3_filename = resource("test.mp3")
m4a_filename = resource("test.m4a")
flac_filename = resource("test.flac")
wav_filename = resource("error.wav")
aiff_filename = resource("error.aiff")
missing_filename = resource("missing.mp3")
mixxxdb_filename = resource("mixxxdb.sqlite")


rename_json_filename = resource("rename.json")
mp3_rename_before_filename = resource("test_rename.mp3")
mp3_rename_after_filename = resource("flavour-town.mp3")


def get_audio_fullname(filename):
    return os.path.join(os.getcwd(), filename)


def reset_tags(*audio_filenames):
    if isinstance(audio_filenames, str):
        audio_filenames = [audio_filenames]

    for audio_filename in audio_filenames:
        tags = EasyFileUtils.read_tags_from_existing(audio_filename)
        MetaDataTagUtils.clear_all_specified_metadata(tags, AUDIO_FILE_METADATA_FIELDS)
        MetaDataTagUtils.add_metadata_tags(tags, "xxx", AUDIO_FILE_METADATA_FIELDS)
        EasyFileUtils.write_tags_to_files(tags)
        new_tags = EasyFileUtils.read_tags_from_existing([audio_filename])
        print(new_tags)
        assert new_tags == [
            {
                "filename": os.path.basename(audio_filename),
                "_filename": get_audio_fullname(audio_filename),
                "album": "xxx",
                "title": "xxx",
                "artist": "xxx",
                "genre": "xxx",
                "comment": "xxx",
            }
        ]


def nuke_output_dir():
    shutil.rmtree(output_dir, ignore_errors=True)


def rm_file(filename):
    try:
        os.remove(mp3_rename_before_filename)
    except FileNotFoundError:
        ...


def reset_rename():
    """
    For testing the rename functionality.
    """
    rm_file(mp3_rename_before_filename)
    rm_file(mp3_rename_after_filename)
    shutil.copy(mp3_filename, mp3_rename_before_filename)


class CmdTests(TestCase):
    def test_restore_metadata_tags_from_backup__is_successful(self):
        """
        FUTURE: include other filetypes beyond mp3.
        """
        reset_tags(
            mp3_filename, m4a_filename, flac_filename
        )  # Ensure test audio file is in an expected state

        cmd.restore_metadata_tags_from_backup(json_backup_filename)
        result = EasyFileUtils.read_tags_from_existing(
            [mp3_filename, m4a_filename, flac_filename]
        )
        assert drop_keys(result, "_filename") == [
            {
                "filename": "test.mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#g2 #genre",
                "comment": "@comment",
            },
            {
                "filename": "test.m4a",
                "title": "title",
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "genre": "#g2 #genre",
            },
            {
                "filename": "test.flac",
                "album": "album",
                "title": "title",
                "genre": "#g2 #genre",
                "artist": "artist",
                "comment": "",
            },
        ]

    def test_create_backup__with_mixxx__is_successfull(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = output_dir
        cmd.create_backup(library_type, mixxxdb_filename, output_directory)
        backup_file = os.listdir(output_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(output_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.mp3",
                "genre": "#g2 #genre",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.m4a",
                "genre": "#g2 #genre",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "",
                "filename": "test.flac",
                "genre": "#g2 #genre",
                "title": "title",
            },
        ]

        backup_error_file = os.listdir(output_dir)[1]
        results = EasyFileUtils.read_json_file(
            os.path.join(output_dir, backup_error_file)
        )
        assert results == {
            "failed": [resource(wav_filename)],
            "missing": [resource(missing_filename)],
        }

    def test_generate_metadata_tags_from_library(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = output_dir
        cmd.generate_metadata_tags_from_library(
            library_type, mixxxdb_filename, output_directory
        )
        backup_file = os.listdir(output_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(output_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.mp3",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.m4a",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.flac",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "error.wav",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "missing.mp3",
                "genre": "!abc #dnb",
                "title": "title",
            },
        ]

    @skip("Deprecated - renaming is more complicated than this when it comes to software recognizing file name changes")
    def test_rename_files(self):
        reset_rename()
        cmd.apply_renaming_to_files(rename_json_filename)
        results = EasyFileUtils.read_tags_from_existing(mp3_rename_after_filename)
        assert drop_keys(results, "_filename") == [
            {
                "filename": "flavour-town.mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#g2 #genre",
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
            mp3_filename, m4a_filename, flac_filename
        )  # Ensure test audio file is in an expected state

        runner = CliRunner()
        results = runner.invoke(main, ["apply", "--json-file", json_backup_filename])
        assert results.exit_code == 0

        result = EasyFileUtils.read_tags_from_existing(
            [mp3_filename, m4a_filename, flac_filename]
        )
        assert drop_keys(result, "_filename") == [
            {
                "filename": "test.mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#g2 #genre",
                "comment": "@comment",
            },
            {
                "filename": "test.m4a",
                "title": "title",
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "genre": "#g2 #genre",
            },
            {
                "filename": "test.flac",
                "album": "album",
                "comment": "",
                "artist": "artist",
                "title": "title",
                "genre": "#g2 #genre",
            },
        ]

    def test__backup__is_successfull(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = output_dir

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

        backup_file = os.listdir(output_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(output_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.mp3",
                "genre": "#g2 #genre",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.m4a",
                "genre": "#g2 #genre",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "",
                "filename": "test.flac",
                "genre": "#g2 #genre",
                "title": "title",
            },
        ]

    def test_make_tags__is_successful(self):
        nuke_output_dir()
        library_type = "mixxx"
        output_directory = output_dir

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

        backup_file = os.listdir(output_dir)[0]
        results = EasyFileUtils.read_json_file(os.path.join(output_dir, backup_file))
        assert drop_keys(results, ["_filename"]) == [
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.mp3",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.m4a",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "test.flac",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "error.wav",
                "genre": "!abc #dnb",
                "title": "title",
            },
            {
                "album": "album",
                "artist": "artist",
                "comment": "@comment",
                "filename": "missing.mp3",
                "genre": "!abc #dnb",
                "title": "title",
            },
        ]

    def test_rename_files(self):
        reset_rename()

        runner = CliRunner()
        results = runner.invoke(main, ["rename", "--json-file", rename_json_filename])
        assert results.exit_code == 0

        results = EasyFileUtils.read_tags_from_existing(mp3_rename_after_filename)
        assert drop_keys(results, "_filename") == [
            {
                "filename": "flavour-town.mp3",
                "album": "album",
                "title": "title",
                "artist": "artist",
                "genre": "#g2 #genre",
                "comment": "@comment",
            }
        ]

    ...
