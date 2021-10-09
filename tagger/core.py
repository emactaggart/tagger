import json
import os
from datetime import datetime
import re

from mutagen import flac, mp4
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from tagger.utils import absolute_path, drop_falsy, first, keep_keys

##### vars & config

SUPPORTED_FILE_TYPES = [".mp3", ".m4a", ".flac"]

AUDIO_FILE_METADATA_FIELDS = [
    "title",
    "artist",
    "album",
    "comment",
    "genre",
    # "key",
    # "bpm"
]

AUDIO_FILE_EXTRAS = [
    "_filename",  # NOTE: used to check compare for changed filenames
    "directory",
    "filename",
    "type",
]


SYMBOL_CHARS = tuple(
    """! " # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7 8 9 : ; < = > ? @ [ \\ ] ^ _ ` { | } ~""".split(
        " "
    )
)
# / is-less-than 0
# 9 is-less-than :
# @ is-less-than A
# Z is-less-than [
# z is-less-than {


def do_setup():
    """
    Setup EasyID3 tags for compatibility with comments. From what I've seen in
    my limited research (Traktor, RekordBox, Serato, Mixxx, EasyTag), typically
    comments are defines as `comment_eng` or `comment_nil` tags. It seems most
    software is compatable with either, a couple defaulting to `comment_eng`.
    We'll try this for now, and adjust if more complicated logic is required
    later.
    """

    comment_nil = "COMM::\x00\x00\x00"
    comment_eng = "COMM::eng"

    def comment_getter(id3, key):
        """
        TODO for edge cases where both comment_eng and comment_nil are populated, show we always return eng?
        """
        return list(id3.get(comment_nil) or id3[comment_eng])

    def comment_setter(id3, key, value):
        """Always defaulting to COMM::eng, removing COMM::\x00\x00\x00 if set."""
        try:
            del id3[comment_nil]
        except KeyError:
            ...

        try:
            frame = id3[comment_eng]
        except KeyError:
            from mutagen.id3._frames import COMM

            # id3.add(mutagen._frames.Frames["COMM"](encoding=3, text=value, lang="eng"))
            id3.add(COMM(encoding=3, text=value, lang="eng"))
        else:
            frame.encoding = 3
            frame.text = value

    def comment_deleter(id3, key):
        try:
            del id3[comment_nil]
        except KeyError:
            ...
        del id3[comment_eng]

    EasyID3.RegisterKey("comment", comment_getter, comment_setter, comment_deleter)


do_setup()


##### Core


class EasyFileUtils:
    """
    Regarding metadata_tags: basically a dict containing a file's metadata which
    can be passed around, molded, and stored easier than file handlers directly
    ex.
    metadata_tags = [
        {
            "filename": "song.mp3",
            "_filename": "/home/username/Music/song.mp3",
            "album": "the album",
            "title": "the title",
            "artist": "the artist",
            "genre": "the genre",
            "comment": "a comment"
        },
        ...,
    ]
    """

    @staticmethod
    def read_tags_from_existing(filenames):
        metadata_tags, _, _ = EasyFileUtils.read_tags_from_filenames(filenames)
        return metadata_tags

    @staticmethod
    def read_tags_from_filenames(filenames):
        """
        Given a list of filenames, read each file and generate an EasyDict from their metadata tags.
        FIXME
        - performance; memory? Are these files even closed properly?
        """
        if isinstance(filenames, str):
            filenames = [filenames]
        filenames = [absolute_path(name) for name in filenames]
        easy_files = []
        failed = []
        missing = []
        for name in filenames:
            try:
                file = EasyFileUtils._open_mp3_or_mp4_or_flac(name)
                easy_files.append(file)
            except TypeError:
                failed.append(name)
            except FileNotFoundError:
                missing.append(name)
        metadata_tags = [EasyFileUtils._easy_file_to_dict(ef) for ef in easy_files]
        return metadata_tags, failed, missing

    @staticmethod
    def read_tags_from_tags(metadata_tags):
        """
        Grab the filenames from each metadata tag and fetch the metadata that's actually in the file.
        FIXME naming
        """
        filenames = [tag["_filename"] for tag in metadata_tags]
        track_metadata_tags, failed, missing = EasyFileUtils.read_tags_from_filenames(
            filenames
        )
        return track_metadata_tags, failed, missing

    @staticmethod
    def write_tags_to_files(metadata_tags, path_replacements=None):
        """
        Given a list of modified EasyDicts, write metadata fields to corresponding audio files (via easy_dict['_filename'])
        `path_replacements` are a list of tuples to rewrite the paths of filenames in the case of swapping file systems. This allows advanced users to apply tags the were generated on a different machine (assuming the new [un]adjusted file paths all line up.)

        """
        if path_replacements:
            for tag in metadata_tags:
                for (path, replacement) in path_replacements:
                    if tag['_filename'].startswith(path):
                        tag['_filename'] = tag['_filename'].replace(path, replacement, 1)
        track_metadata_tags, _, _ = EasyFileUtils.read_tags_from_tags(metadata_tags)
        updated_tags = MetaDataTagUtils.find_updated_tags(
            metadata_tags, track_metadata_tags
        )
        easy_files, failed, missing = EasyFileUtils._dicts_to_easy_files(metadata_tags=updated_tags)
        print(
            "Total %s file tags found. %s tags require updating..."
            % (len(track_metadata_tags), len(easy_files))
        )
        if failed:
            print("Failed", failed)
        if missing:
            print("Missing: ", missing)
        for i, e in enumerate(easy_files):
            if i % 100 == 0:
                print("%s of %s..." % (i, len(easy_files)))
            e.save()
        print("DINNERS READY")

    @staticmethod
    def rename_files(metadata_tags):
        """
        FIXME
        - performance
        - Fail safe
        """
        renamed = [
            d
            for d in metadata_tags
            if os.path.basename(d["_filename"]) != d["filename"]
        ]

        for r in renamed:
            new_filename = r["filename"]
            previous_absolute = r["_filename"]
            previous_dir = os.path.dirname(previous_absolute) + "/"
            os.rename(previous_absolute, previous_dir + new_filename)


    @staticmethod
    def export_tags_to_file(
            output_directory, output_filename, metadata_tags, failed=None, missing=None
    ):
        """
        NOTE: This will remove unrelated/unwanted information from `metadata_tags`.
        """
        metadata_tags = MetaDataTagUtils.remove_unnecessary_tags(metadata_tags)
        tags_filename = os.path.join(
            output_directory,
            output_filename
        )
        EasyFileUtils.write_json_file(tags_filename, metadata_tags)
        if not failed:
            failed = []
        if not missing:
            missing = []
        if failed or missing:
            errors_filename = os.path.join(
                output_directory,
                os.path.splitext(output_filename)[0] + "-errors" + os.path.splitext(output_filename)[1]
            )
            EasyFileUtils.write_json_file(
                errors_filename,
                {
                    "failed": [f.replace("\\", "/") for f in failed],
                    "missing": [f.replace("\\", "/") for f in missing],
                },
            )
        return tags_filename

    @staticmethod
    def make_filename(prefix="export"):
        timestamp_str = datetime.now().strftime("%Y-%m-%dT%H-%M")
        return "%s-tags-%s.json" % (prefix, timestamp_str)


    @staticmethod
    def read_json_file(json_filename):
        """
        Given a json file, open and return it's parsed contents.
        """
        with open(absolute_path(json_filename), "r") as json_file:
            file_contents = json_file.read()
        json_content = json.loads(file_contents)
        return json_content

    @staticmethod
    def write_json_file(json_filename, json_content):
        """
        Given `json_content` convert it to a string and write to the given `json_filename`.
        """
        json_filename = absolute_path(json_filename)
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        json_str = json.dumps(json_content, indent=2, sort_keys=True)
        with open(json_filename, "w") as json_file:
            json_file.write(json_str)
        return json_filename

    @classmethod
    def _dicts_to_easy_files(cls, metadata_tags):
        """
        Using the details provided in the easy dict, open the corresponding
        audio file and set the metadata tags to match those provided in the
        dict. NOTE This does not write to the file yet.
        """
        if isinstance(metadata_tags, dict):
            metadata_tags = [metadata_tags]
        easy_files = []
        failed = []
        missing = []
        for tag in metadata_tags:
            easy_file = None
            try:
                easy_file = EasyFileUtils._open_mp3_or_mp4_or_flac(filename=tag["_filename"])
                easy_files.append(easy_file)
            except TypeError:
                failed.append(tag["_filename"])
            except FileNotFoundError:
                missing.append(tag["_filename"])
            for k in AUDIO_FILE_METADATA_FIELDS:
                easy_file[k] = tag.get(k) or ""
        return easy_files, failed, missing

    @staticmethod
    def _easy_file_to_dict(easy_file):
        """Create an easy dict from a given mutagen based file handler/easy_file."""
        absolute_name = easy_file.filename
        easy_dict = {
            "filename": os.path.basename(absolute_name),
            "_filename": absolute_name,
            # "ext": os.path.splitext(absolute_name)[1],
            **{
                k: first(v)
                for k, v in easy_file.items()
                if k in AUDIO_FILE_METADATA_FIELDS
            },
        }
        return easy_dict

    @staticmethod
    def _open_mp3_or_mp4_or_flac(filename):
        """
        Given a filename open the file using the most suitable mutagen file handler type.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
        ext = os.path.splitext(filename)[1]
        # TODO patch in dict of SUPPORTED_FILE_TYPES
        # audio_file = SUPPORTED_FILE_MAP[ext](filename) # default_dict
        if ext == ".mp3":
            return EasyID3(filename)
        elif ext == ".m4a":
            return EasyMP4(filename)
        elif ext == ".flac":
            return flac.FLAC(filename)
        else:
            raise TypeError(ext)


class MetaDataTagUtils:
    """For mangling file metadata via their corresponding metadata_tags"""

    @staticmethod
    def tag_logic(tags):
        """
        We only want to write specific tags to the genre tag. These typically begin with sumbols
        """
        is_permitted = lambda x: x.startswith(SYMBOL_CHARS)
        return [tag for tag in tags if is_permitted(tag)]

    @staticmethod
    def map_to_metadata_tags(db_tags):
        metadata_tags = [
            {
                **ed,
                "genre": " ".join(MetaDataTagUtils.tag_logic(ed["crates"])),
            }
            for ed in db_tags
        ]
        return metadata_tags

    @staticmethod
    def remove_unnecessary_tags(metadata_tags):
        necessary_tags = [*AUDIO_FILE_METADATA_FIELDS, *AUDIO_FILE_EXTRAS]
        for t in metadata_tags:
            # fix weird windows backslashes instead of forward slashes
            t["_filename"] = t["_filename"].replace("\\", "/")
        return keep_keys(metadata_tags, necessary_tags)

    @staticmethod
    def find_updated_tags(tags_a, tags_b):
        seta = set(frozenset(t.items()) for t in drop_falsy(tags_a))
        setb = set(frozenset(t.items()) for t in drop_falsy(tags_b))
        results = set.difference(seta, setb)
        results_dict = list(map(dict, results))
        return results_dict

    @classmethod
    def add_metadata_tags(
        cls, metadata_tags, tag_name, metadata_fields, remove_tag=False
    ):
        """
        FIXME rename add tags to metadata fields
        Add (or remove) tags to metadata field for given list of dicts.
        FIXME example
        FIXME provide more details on error
        """
        if isinstance(metadata_fields, str):
            metadata_fields = [metadata_fields]
        cls.validate_metadata_fields(metadata_fields)
        tagger_fn = cls.remove_tag_fn if remove_tag else cls.add_tag_fn
        for af in metadata_tags:
            for field in metadata_fields:
                af[field] = tagger_fn(af.get(field) or "", tag_name)

    @classmethod
    def clear_all_specified_metadata(cls, metadata_tags, metadata_fields):
        """
        Clear a given metadata field from all metadata_tags.
        NOTE: this modifies the `metadata_tags`

        `metadata_fields` - a string or list of strings representing metadata fields
        FIXME example
        FIXME provide more details on error
        """
        if isinstance(metadata_fields, str):
            metadata_fields = [metadata_fields]
        cls.validate_metadata_fields(metadata_fields)
        for af in metadata_tags:
            for field in metadata_fields:
                af[field] = ""

    @staticmethod
    def validate_metadata_fields(metadata_fields):
        """
        Verify that only we're only updating metadata fields from our expected
        list, and not others that are not (at least initially) intended to be
        modified.
        ex.
        MetaDataTagUtils.validate_metadata_fields(["wow"])
        => ValueError(...)
        """
        invalid_fields = [
            f for f in metadata_fields if f not in AUDIO_FILE_METADATA_FIELDS
        ]
        if len(invalid_fields) > 0:
            raise ValueError(
                "Invalid metadata name %s, must be one of: %s"
                % (invalid_fields, AUDIO_FILE_METADATA_FIELDS)
            )

    @staticmethod
    def add_tag_fn(metadata, tag):
        """
        Add the string `tag` to the stringified list of tags contained in `metadata`. Re-stringify the results.
        NOTE it is recommended that `tag` be prefixed with a symbol, this is not automatically done here.
        ex.
        MetaDataTagUtils.add_tag_fn("#dnb #bass", "#pop")
        => "#bass #dnb #pop"
        """
        if not metadata:
            return tag
        tags = metadata.strip().split()
        if tag not in tags:
            tags.append(tag)
        return " ".join(sorted(tags))

    @staticmethod
    def remove_tag_fn(metadata, tag):
        """
        Remove the string `tag` from the stringified list of tags contained in the `metadata`. Re-stringify the results.
        NOTE `tag` must be an exact match, if there are missing "#" (or symbols) then the tag will not be removed
        ex.
        MetaDataTagUtils.remove_tag_fn("#dnb #bass #pop", "#pop")
        => "#bass #dnb"
        """
        if not metadata:
            return ""
        tags = metadata.strip().split()
        return " ".join(sorted([t for t in tags if t != tag]))
