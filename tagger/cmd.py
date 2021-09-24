import os
from tagger.core import EasyFileUtils, MetaDataTagUtils
from tagger import mixxx, serato


class LibraryType:
    mixxx = "mixxx"
    serato = "serato" # XXX verify this works via command line; write tests
    # rekordbox
    # traktor

    @classmethod
    def all(cls):
        return [cls.mixxx, cls.serato]


def restore_metadata_tags_from_backup(json_filename, path_replacements=None):
    """
    Read the tags from a backed up json file and write them to the corresponding audio files.
    """
    metadata_tags = EasyFileUtils.read_json_file(json_filename)
    EasyFileUtils.write_tags_to_files(metadata_tags, path_replacements)


def create_backup(library_type, library_path, output_directory, output_filename=None):
    output_filename = output_filename or  EasyFileUtils.make_filename("backup")
    if library_type == LibraryType.mixxx:
        database_filename = library_path
        mixxx_tags = mixxx.tags_from_library(database_filename)
        metadata_tags, failed, missing = EasyFileUtils.read_tags_from_tags(mixxx_tags)
        out_file =  EasyFileUtils.export_tags_to_file(output_directory, output_filename,  metadata_tags, failed, missing)
    elif library_type == LibraryType.serato:
        serato_directory = library_path
        serato_tags = serato.tags_from_library(serato_directory)
        metadata_tags, failed, missing = EasyFileUtils.read_tags_from_tags(serato_tags)
        out_file =  EasyFileUtils.export_tags_to_file(output_directory, output_filename, metadata_tags, failed, missing)
    else:
        raise ValueError("Invalid `library_type`.")
    return out_file


def generate_metadata_tags_from_library(
        library_type, library_path, output_directory, output_filename=None
):
    output_filename = output_filename or EasyFileUtils.make_filename()
    if library_type == LibraryType.mixxx:
        datebase_filename = library_path
        mixxx_tags = mixxx.tags_from_library(datebase_filename)
        metadata_tags = MetaDataTagUtils.map_to_metadata_tags(mixxx_tags)
        out_file = EasyFileUtils.export_tags_to_file(output_directory, output_filename, metadata_tags)
    elif library_type == LibraryType.serato:
        serato_directory = library_path
        serato_tags = serato.tags_from_library(serato_directory)
        metadata_tags = MetaDataTagUtils.map_to_metadata_tags(serato_tags)
        out_file =  EasyFileUtils.export_tags_to_file(serato_directory, output_filename, metadata_tags)
    else:
        raise ValueError("Invalid `library_type`.")
    return out_file



def apply_renaming_to_files(json_filename):
    """
    The idea is to edit a json file with your preferred editor which can then be
    used to rename the file's without having to use various dj software or tag
    editors.
    NOTE: this fn is strictly for renaming files, it will not write any changed
    metadata to said files (use `apply_metadata_tags_to_audio_files` instead).

    #FIXME verify this with serato, renaming files will cause them to be missing from serato and like from mixxx too
    """
    metadata_tags = EasyFileUtils.read_json_file(json_filename)
    EasyFileUtils.rename_files(metadata_tags)
