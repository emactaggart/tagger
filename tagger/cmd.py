import os
from tagger.core import EasyFileUtils, MetaDataTagUtils
from tagger import mixxx

class LibraryType:
    mixxx = "mixxx"
    # serato = "serato"
    # rekordbox
    # traktor


def restore_metadata_tags_from_backup(json_filename):
    """
    Read the tags from a backed up json file and write them to the corresponding audio files.
    """
    metadata_tags = EasyFileUtils.read_json_file(json_filename)
    EasyFileUtils.write_tags_to_files(metadata_tags)


def create_backup(library_type, library_path, output_directory):
    if library_type == LibraryType.mixxx:
        database_filename = library_path
        mixxx_tags = mixxx.tags_from_library(database_filename)
        track_metadata_tags, failed, missing = EasyFileUtils.read_tags_from_tags(mixxx_tags)
        EasyFileUtils.export_tags_to_file(output_directory, track_metadata_tags, failed, missing, "backup")
    else:
        raise ValueError("Invalid `library_type`.")
    ...


def generate_metadata_tags_from_library(
    library_type, library_path, metadata_tag_json_output_filename
):
    if library_type == LibraryType.mixxx:
        datebase_filename = library_path
        mixxx_tags = mixxx.tags_from_library(datebase_filename)
        metadata_tags = MetaDataTagUtils.map_to_metadata_tags(mixxx_tags)
        EasyFileUtils.export_tags_to_file(metadata_tag_json_output_filename, metadata_tags)
    else:
        raise ValueError("Invalid `library_type`.")
    ...


def apply_renaming_to_files(json_filename):
    """
    The idea is to edit a json file with your preferred editor which can then be
    used to rename the file's without having to use various dj software or tag
    editors.
    NOTE: this fn is strictly for renaming files, it will not write any changed
    metadata to said files (use `apply_metadata_tags_to_audio_files` instead).
    """
    metadata_tags = EasyFileUtils.read_json_file(json_filename)
    EasyFileUtils.rename_files(metadata_tags)
