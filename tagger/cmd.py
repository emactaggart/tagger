import os
import shutil
from tagger.core import EasyFileUtils, MetaDataTagUtils
from tagger import mixxx, serato
from tagger.utils import absolute_path, keep_keys


class LibraryType:
    mixxx = "mixxx"
    serato = "serato"  # XXX verify this works via command line; write tests
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
    output_filename = output_filename or EasyFileUtils.make_filename("backup")
    if library_type == LibraryType.mixxx:
        database_filename = library_path
        mixxx_tags = mixxx.tags_from_library(database_filename)
        metadata_tags, failed, missing = EasyFileUtils.read_tags_from_tags(mixxx_tags)
        out_file = EasyFileUtils.export_tags_to_file(
            output_directory, output_filename, metadata_tags, failed, missing
        )
    elif library_type == LibraryType.serato:
        serato_directory = library_path
        serato_tags = serato.tags_from_library(serato_directory)
        metadata_tags, failed, missing = EasyFileUtils.read_tags_from_tags(serato_tags)
        out_file = EasyFileUtils.export_tags_to_file(
            output_directory, output_filename, metadata_tags, failed, missing
        )
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
        out_file = EasyFileUtils.export_tags_to_file(
            output_directory, output_filename, metadata_tags
        )
    elif library_type == LibraryType.serato:
        serato_directory = library_path
        serato_tags = serato.tags_from_library(serato_directory)
        metadata_tags = MetaDataTagUtils.map_to_metadata_tags(serato_tags)
        out_file = EasyFileUtils.export_tags_to_file(
            output_directory, output_filename, metadata_tags
        )
    else:
        raise ValueError("Invalid `library_type`.")
    return out_file


def apply_renaming_to_files(json_filename):
    """
    # DEPRECATED

    The idea is to edit a json file with your preferred editor which can then be
    used to rename the file's without having to use various dj software or tag
    editors.
    NOTE: this fn is strictly for renaming files, it will not write any changed
    metadata to said files (use `apply_metadata_tags_to_audio_files` instead).

    #FIXME verify this with serato, renaming files will cause them to be missing from serato and like from mixxx too
    """
    metadata_tags = EasyFileUtils.read_json_file(json_filename)
    EasyFileUtils.rename_files(metadata_tags)


def generate_replacement_json(library_type, library_path, json_filename):
    """
    MIXXX only
    """
    def format_for_replacement(metadata_tags):
        return [{"from": d['_filename'], "to": d['_filename']} for d in metadata_tags]
    database_filename = library_path
    mixxx_tags = mixxx.tags_from_library(database_filename)
    replacement_data = format_for_replacement(mixxx_tags)
    EasyFileUtils.write_json_file(json_filename, replacement_data)
    return json_filename, replacement_data


def relocate_files(library_type, library_path, json_filename, replacement_dir):
    """
    if `replacement_dir` is provided, the files on the system will also be moved, not just relocated in mixxx
    replace_json should be in the form of: [{"from": $FROM$: "to": $TO$}]
    """
    if not replacement_dir or not os.path.isdir(absolute_path(replacement_dir)):
        raise ValueError("Invalid replacement directory.")

    def parse_replacements(replacement_dicts):
        # TODO deal with duplicate replacements?
        # TODO remove empties
        # TODO remove invalid?
        is_valid = lambda a,b: a and b and a != b
        replacement_pairs = [(r["from"], r["to"]) for r in replacement_dicts]
        valid = [(a, b) for a, b in replacement_pairs if is_valid(a, b)]
        invalid = [(a, b) for a, b in replacement_pairs if not is_valid(a,b)]
        return valid, invalid

    def relocate_tracks(replacements):
        for filename_from, filename_to in replacements:
            mixxx.rename_track_locations(library_path, filename_from, filename_to)
        print(f"Relocated {len(replacements)} files")

    def move_files(replacements):
        files_to_replace = [f for f, _ in replacements if os.path.isfile(f)]
        missing_files = [f for f, _ in replacements if not os.path.isfile(f)]
        for f in files_to_replace:
            shutil.move(f, os.path.join(replacement_dir, os.path.basename(f)))
        return files_to_replace, missing_files

    replacements, invalid = parse_replacements(
        replacement_dicts=EasyFileUtils.read_json_file(json_filename)
    )
    print(f"Replacing {len(replacements)} tracks")
    if invalid:
        print(f"Cannot relocated {len(invalid)} tracks as they are invalid: {invalid}")

    relocate_tracks(replacements)

    replaced_files, missing_files = move_files(replacements)
    print(f"Moved {len(replaced_files)} files into {replacement_dir}.")
    print(f"Unable able to move {len(missing_files)} files as they did not exist.", missing_files)

    return replaced_files, missing_files


def find_duplicates_simple(library_type, library_path, json_filename):
    database_filename = library_path
    mixxx_tags = mixxx.tags_from_library(database_filename)
    # find_by_title = lambda title,

    # title == title?
    # title without symbols etc same as title? ["PREMIER", "Original Mix", "(",  ")", "[.*]", "(Audio)"]


# FIXME
def _find_duplicates_complex(library_type, library_path, json_filename):
    database_filename = library_path
    mixxx_tags = mixxx.tags_from_library(database_filename)

    to_name = lambda track: " ".join([track.get('artist') or '', track.get('title') or '']).lower()

    long_enough = lambda name: len(name) > 0
    split_name = lambda name: [section for section in name.split(" ") if long_enough(section)]

    names_files = [(to_name(track), track['_filename']) for track in mixxx_tags]
    split_names_files = [(split_name(track[0]), track[1]) for track in names_files]

    # split_names_files[2]
    # name = names[0]
    # " ".join(["abc", "def"]) in " ".join(["123", "abc", "def", "hij"])


    # how can we detect duplicate looking files?
    # check filename / title / artist?

    # Ideas:
    # - split titles in space
    # - remove words less than 3 characters
    # - insert artist at the beginning of list
    # - find similar sublists containing n (2?) or more
    ...
