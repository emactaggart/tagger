import json
import os
from datetime import datetime

from mutagen import flac, mp4
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from tagger.utils import first, keep_keys

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
    Regarding easy_dicts: basically a dict containing a file's metadata which
    can be passed around, molded, and stored easier than file handlers directly
    ex.
    easy_dicts = [
        {
            "filename": "song.mp3",
            "_filename": "/home/username/Music/song.mp3",
            "ext": ".mp3",
            "album": "the album",
            "title": "the title",
            "artist": "the artist",
            "genre": "the genre",
            "comment": "a comment"
        },
        ...,
    ]
    """

    @classmethod
    def read_tags_from_filenames(cls, filenames):
        """
        Given a list of filenames, read each file and generate an EasyDict from their metadata tags.

        FIXME
        - performance; memory?
        - failsafe, when files do not exist, loud=True?
        """
        if isinstance(filenames, str):
            filenames = [filenames]
        filenames = [os.path.realpath(os.path.expanduser(fn)) for fn in filenames]
        easy_files = [cls._open_mp3_or_mp4_or_flac(fn) for fn in filenames]
        easy_dicts = [cls._easy_file_to_dict(ef) for ef in easy_files]
        return easy_dicts

    @staticmethod
    def write_tags_to_files(easy_dicts):
        """
        Given a list of modified EasyDicts, write metadata fields to corresponding audio files (via easy_dict['_filename'])
        FIXME
        - performance, minimize number of writes? avoid writing timestamps?
        - Fail safe,  when files do not exist, loud=True?
        - improve logging vs printing
        """
        easy_files = [EasyFileUtils._dict_to_easy_file(d) for d in easy_dicts]
        print("Writing tags to %s files." % len(easy_files))
        for i, e in enumerate(easy_files):
            if i % 100 == 0:
                print(i)
            e.save()
        print("DINNERS READY")

    @staticmethod
    def rename_files(easy_dicts):
        """
        FIXME
        - performance
        - Fail safe
        """
        renamed = [
            d for d in easy_dicts if os.path.basename(d["_filename"]) != d["filename"]
        ]

        for r in renamed:
            new_filename = r["filename"]
            previous_absolute = r["_filename"]
            previous_dir = os.path.dirname(previous_absolute) + "/"
            os.rename(previous_absolute, previous_dir + new_filename)

    @staticmethod
    def export_tags_to_file(output_directory, metadata_tags):
        """
        NOTE: This will remove unrelated/unwanted information from `metadata_tags`.
        """
        tag_backup_filename = "track-tags-backup-%s.json" % datetime.now().strftime(
            "%Y-%m-%dT%H-%M"
        )
        json_filename = os.path.join(output_directory, tag_backup_filename)
        metadata_tags = MetaDataTagUtils.remove_unnecessary_tags(metadata_tags)
        EasyFileUtils.write_json_file(json_filename, metadata_tags)

    @staticmethod
    def read_json_file(json_filename):
        """
        Given a json file, open and return it's parsed contents.
        """
        with open(json_filename, "r") as json_file:
            file_contents = json_file.read()
        json_content = json.loads(file_contents)
        return json_content

    @staticmethod
    def write_json_file(json_filename, json_content):
        """
        Given `json_content` convert it to a string and write to the given `json_filename`.
        """
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        json_str = json.dumps(json_content)
        with open(json_filename, "w") as json_file:
            json_file.write(json_str)
        return json_filename

    @classmethod
    def _dict_to_easy_file(cls, easy_dict):
        """
        Using the details provided in the easy dict, open the corresponding
        audio file and set the metadata tags to match those provided in the
        dict. NOTE This does not write to the file yet.
        """
        easy_file = cls._open_mp3_or_mp4_or_flac(easy_dict["_filename"])
        for k in AUDIO_FILE_METADATA_FIELDS:
            easy_file[k] = easy_dict.get(k, "")
        return easy_file

    @staticmethod
    def _easy_file_to_dict(easy_file):
        """Create an easy dict from a given mutagen based file handler/easy_file."""
        absolute_name = easy_file.filename
        easy_dict = {
            "filename": os.path.basename(absolute_name),
            "_filename": absolute_name,
            "ext": os.path.splitext(absolute_name)[1],
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
            raise Exception("Invalid file or file does not exist: %s" % filename)
        ext = os.path.splitext(filename)[1]
        # TODO patch in dict of SUPPORTED_FILE_TYPES
        # audio_file = SUPPORTED_FILE_MAP[ext](filename) # default_dict
        if ext == ".mp3":
            return EasyID3(filename)
        elif ext == ".m4a":
            try:
                return EasyMP4(filename)
            except mp4.MP4StreamInfoError as e:
                raise Exception("Invalid Mp4: %s" % filename)
        elif ext == ".flac":
            return flac.FLAC(filename)
        else:
            raise Exception("Invalid file type: %s" % filename)


class MetaDataTagUtils:
    """For mangling file metadata via their corresponding easy_dicts"""

    @staticmethod
    def map_to_metadata_tags(db_tags):
        """
        """
        metadata_tags = [{
            **ed,
            "genre": "".join(ed['crates']),
            "comment": "".join(ed["playlists"])
        } for ed in db_tags]
        return metadata_tags

    @staticmethod
    def remove_unnecessary_tags(metadata_tags):
        necessary_tags = [*AUDIO_FILE_METADATA_FIELDS, *AUDIO_FILE_EXTRAS]
        return keep_keys(metadata_tags, necessary_tags)

    @classmethod
    def add_metadata_tags(cls, easy_dicts, tag_name, metadata_fields, remove_tag=False):
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
        for af in easy_dicts:
            for field in metadata_fields:
                af[field] = tagger_fn(af.get(field) or "", tag_name)

    @classmethod
    def clear_all_specified_metadata(cls, easy_dicts, metadata_fields):
        """
        Clear a given metadata field from all easy_dicts.
        NOTE: this modifies the `easy_dicts`

        `metadata_fields` - a string or list of strings representing metadata fields
        FIXME example
        FIXME provide more details on error
        """
        if isinstance(metadata_fields, str):
            metadata_fields = [metadata_fields]
        cls.validate_metadata_fields(metadata_fields)
        for af in easy_dicts:
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
