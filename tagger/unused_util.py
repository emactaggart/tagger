from collections import namedtuple
import os

from mutagen import mp4
from tagger.core import first
from tagger.core import AUDIO_FILE_METADATA_FIELDS


##### Audio File Browsing Utilities
# Unused code that may help in understanding where metadata is store on specific
# file types. Primarily to be used for testing and investigating.


AudioTags = namedtuple("AudioTags", AUDIO_FILE_METADATA_FIELDS)

# NOTE these audio tags may only be required for examining raw tags. It "seems" to be much easier to edit tags via EasyID3 and EasyMP4
Mp3AudioTags = AudioTags(
    **{
        "album": "TALB",
        "artist": "TPE1",
        "comment": "COMM::eng",  # or "COMM::\x00\x00\x00"
        "genre": "TCON",
        "title": "TIT2",
        # "bpm": "TBPM",
        # "key": "TKEY",
    }
)

Mp4AudioTags = AudioTags(
    **{
        "album": "©alb",
        "artist": "©ART",
        "comment": "©cmt",
        "genre": "©gen",
        "title": "©nam",
        # "bpm": "tmpo",
        # "key": "----:com.apple.iTunes:initialkey",
    }
)

FlacAudioTags = AudioTags(
    **{
        "album": "album",
        "artist": "artist",
        "comment": "comment",
        "genre": "genre",
        "title": "title",
    }
)


class Mp3Utils:
    "Intended for investigating available tags"

    @staticmethod
    def to_keys(fmp3):
        return [k[:20] for k in fmp3.keys()]

    @staticmethod
    def as_dict(fmp3):
        text_or_desc = (
            lambda txxx: first(getattr(txxx, "text", None))
            or getattr(txxx, "desc", None)
            or "N/A"
        )
        return {k: text_or_desc(v) for k, v in fmp3.items() if "TRAKTOR" not in k}

    @classmethod
    def all_comments(cls, fmp3):
        return {k: v for k, v in cls.as_dict(fmp3).items() if k.startswith("COMM")}


class Mp4Utils:
    "Intended for investigating available tags"

    @staticmethod
    def to_keys(fmp4):
        return [k for k in fmp4.keys()]

    @staticmethod
    def as_dict(fmp4):
        max_bytes_length = 20
        id_or_to_bytes = (
            lambda v: bytes(v)[:max_bytes_length]
            if isinstance(v, mp4.MP4FreeForm)
            else v
        )
        return {k: id_or_to_bytes(first(v)) for k, v in fmp4.items()}

    @classmethod
    def all_comments(cls, fmp4):
        return {k: v for k, v in cls.as_dict(fmp4).items() if k.startswith("COMM")}


class FlacUtils:
    "Intended for investigating available tags"

    @staticmethod
    def to_keys(fflac):
        return [k for k in fflac.keys()]

    @staticmethod
    def as_dict(fflac):
        max_bytes_length = 20
        # id_or_to_bytes  = lambda v: bytes(v)[:max_bytes_length] if isinstance(v, mp4.MP4FreeForm) else v
        # return {k: id_or_to_bytes(first(v)) for k,v in fflac.items()}
        return {k: first(v) for k, v in fflac.items()}

    @classmethod
    def all_comments(cls, fflac):
        return {k: v for k, v in cls.as_dict(fflac).items() if k == "COMMENT"}


##### Traktor Utils

class TraktorUtils():
    "Traktor likes to put funky data in weird places"

    def contains_traktor_tag(mutagen_file):
        for k in mutagen_file.keys():
            if k.startswith("PRIV:TRAKTOR4"):
                return True
        return False

    def head_traktor_tag(mutagen_file):
        for k in mutagen_file.keys():
            if k.startswith("PRIV:TRAKTOR4"):
                return k[:500]
        return None

    def del_traktor_tag(mutagen_file):
        """Delete annoying traktor tags
        NOTE: this will save changes made to this file"""
        key_to_delete = None
        for k in mutagen_file.keys():
            if k.startswith("PRIV:TRAKTOR4"):
                key_to_delete = k
                break
        if not key_to_delete:
            return False

        del mutagen_file[key_to_delete]
        mutagen_file.save()
        return True


class UnusedJunk:

    # @classmethod
    # def read_all_tags_from_dir(cls, dir_name):
    #     """
    #     Grab tags from directory, return easy_dicts
    #     """
    #     filenames = FileDiscoveryUtils.dir_search(dir_name)
    #     easy_dicts = EasyFileUtils.read_tags_from_filenames(filenames)
    #     return easy_dicts

    # @classmethod
    # def tag_metadata_m3u(cls, m3u_filename, tag_name, metadata_name, remove_tags=False):
    #     """Given a playlist file, add or remove given tag_name in given metadata field."""
    #     # FIXME deprecate
    #     filenames = FileDiscoveryUtils.open_m3u(m3u_filename)
    #     easy_dicts = EasyFileUtils.read_tags_from_filenames(filenames)
    #     MetaDataTagUtils.add_metadata_tags(
    #         easy_dicts, tag_name, metadata_name, remove_tags
    #     )
    #     # easy_dicts = [
    #     #     {**ed, metadata_name: MetaDataTagUtils.add_tag(ed.get("metadata"))} for ed in easy_dicts
    #     # ]
    #     EasyFileUtils.write_tags_to_files(easy_dicts)


    # @classmethod
    # def clear_metadata_dir(cls, directory, metadata_name):
    #     """Clear all the comment tags for tracks in a given directory"""
    #     # FIXME deprecate
    #     filenames = FileDiscoveryUtils.dir_search(directory)
    #     easy_dicts = EasyFileUtils.read_tags_from_filenames(filenames)
    #     MetaDataTagUtils.clear_all_specified_metadata(easy_dicts, metadata_name)
    #     EasyFileUtils.write_tags_to_files(easy_dicts)

    # @staticmethod
    # def _open_dir(directory):
    #     """Return a list of audio file names in a given directory"""
    #     if not os.path.isdir(directory):
    #         raise Exception("Invalid directory: %s" % directory)
    #     if not directory.endswith("/"):
    #         directory = directory + "/"
    #     filenames_raw = os.listdir(directory)
    #     relative_filenames = [
    #         fn
    #         for fn in filenames_raw
    #         if os.path.splitext(fn)[1] in SUPPORTED_FILE_TYPES
    #     ]
    #     audio_filenames = [directory + fn for fn in relative_filenames]
    #     return audio_filenames

    # @staticmethod
    # def _open_m3u(m3u_filename):
    #     """
    #     Open m3u file and grab all the filenames making sure the files all exist.
    #     NOTE:
    #     - the file doesn't actually have to be a properly formatted .m3u
    #     WARNING:
    #     - undefined behaviour for songs with relative path names (ex. ../Music/my-song.mp3), use absolute instead (ex. /home/ur-name/Music/my-song.mp3)
    #     """
    #     if not os.path.isfile(m3u_filename):
    #         raise Exception("Invalid file or file does not exist: %s" % m3u_filename)
    #     with open(m3u_filename, "r") as f:
    #         filenames_raw = f.readlines()
    #     no_newlines = [fn[:-1] for fn in filenames_raw]  # Windows compatible?
    #     filenames = [fn for fn in no_newlines if not fn.startswith("#")]
    #     existing_filenames = []
    #     for f in filenames:
    #         if os.path.isfile(f):
    #             existing_filenames.append(f)
    #         else:
    #             print("File does not exist. m3u: %s, filename: %s" % (m3u_filename, f))
    #     return existing_filenames


    ...


# import os
# from datetime import datetime
# from tagger.util import JsonUtils
# from tagger.core import EasyFileUtils, FileDiscoveryUtils


# class TagableTypes:
#     file = "file"
#     dir = "dir"
#     recursive_dir = "recursive-dir"
#     m3u = "m3u"

#     @classmethod
#     def all(cls):
#         return [cls.file, cls.dir, cls.recursive_dir, cls.m3u]


class TaggerCommands:
    """
    FLOW:
    file | dir | m3u | files | nested-dir -> easy_dicts

    easy_dicts -> json
    """

    @staticmethod
    def collect_filenames(*file_things):
        """
        Given a list of different `file_things`, collect all of the filenames depending on the type of thing
        Where a `file_thing` to back up is a tuple of (`file_thing_name`, `file_thing_type`)
        """
        # things = [
        #     ("filename.mp3", "file"),
        #     # (["filename-1.mp3", "filename-2.mp3"], "multiple-files"), # TODO what about list of dirs?
        #     ("playlist.m3u", "m3u"),
        #     ("my_dir", "dir"),
        #     ("my_rec_dir", "recursive-dir"),
        # ]

        mapper = {
            TagableTypes.file: lambda thing: [thing],
            TagableTypes.m3u: FileDiscoveryUtils.open_m3u,
            TagableTypes.dir: FileDiscoveryUtils.dir_search,
            TagableTypes.recursive_dir: FileDiscoveryUtils.recursive_dir_search
            # "multiple-files"
            # "multiple-dirs"
            # "multiple-m3us"
            # "previous-json-tags-backup-file": ... # TODO
        }
        filenames = []
        for file_thing_name, file_thing_type in file_things:
            filenames.extend(mapper[file_thing_type](file_thing_name))
        return filenames

        @classmethod
        def backup_tags(cls, backup_location, *file_things_to_backup, backup_filename=None):
            """
            Where a `file_thing` to back up is a tuple of (`file_thing_name`, `file_thing_type`)
            """
            filenames = cls.collect_filenames(file_things_to_backup)
            tags = EasyFileUtils.read_tags_from_filenames(filenames)

            now_up_to_minutes = datetime.isoformat(datetime.now())[:16]
            backup_fullname = os.path.join(
                backup_location, backup_filename or now_up_to_minutes
            )
            JsonUtils.write_json_file(backup_fullname, tags)
            return backup_fullname, len(tags)

    #     @staticmethod
    #     def restore_from_backup(json_filename):
    #         tags = JsonUtils.read_json_file(json_filename)
    #         EasyFileUtils.write_tags_to_files(tags)

    ...


class FileDiscoveryUtils:
    @staticmethod
    def open_m3u(m3u_filename):
        """
        Open m3u file and grab all the filenames making sure the files all exist.

        NOTE:
        - the file doesn't actually have to be a properly formatted .m3u
        WARNING:
        - undefined behaviour for songs with relative path names (ex. ../Music/my-song.mp3), use absolute instead (ex. /home/ur-name/Music/my-song.mp3)
        """
        if not os.path.isfile(m3u_filename):
            raise Exception("Invalid file or file does not exist: %s" % m3u_filename)

        with open(m3u_filename, "r") as f:
            filenames_raw = f.readlines()

        no_newlines = [fn[:-1] for fn in filenames_raw]  # Windows compatible?
        filenames = [fn for fn in no_newlines if not fn.startswith("#")]

        existing_filenames = []
        for f in filenames:
            if os.path.isfile(f):
                existing_filenames.append(f)
            else:
                print("File does not exist. m3u: %s, filename: %s" % (m3u_filename, f))

        return existing_filenames

    @classmethod
    def recursive_dir_search(dirpath):
        return cls.dir_search(dirpath, recursive=True)

    @staticmethod
    def dir_search(dirpath, recursive=False):
        absolute_dirpath = os.path.realpath(os.path.expanduser(dirpath))
        if recursive:
            search_dir = "%s/**/*" % (absolute_dirpath)
        else:
            search_dir = "%s/*" % (absolute_dirpath)
        filenames = []
        for file_type in SUPPORTED_FILE_TYPES:
            filenames.extend(glob.glob("%s%s" % (search_dir, file_type)))
        return filenames


class TagsFns:
    """
    NOTE: this may come into use in the advent of in-python tag merging instead of using sql
    """

    def pairs_to_tag_dicts(pairs):
        """
        `pairs` - (playlist_or_crate_name, filename) tuples generated from
        MixxUtils.get_all_tracks_grouped_by_<playlists/creates>
        Returns
        {
          'filename': filename,
          'tags': {set-of-tagnames}
        }
        """
        filenames = list(map(itemgetter(1), pairs))
        filename_tag_dicts = [
            {
                "filename": filename,
                "tags": {pair[0] for pair in pairs if pair[1] == filename},
            }
            for filename in filenames
            if filename is not None
        ]
        return filename_tag_dicts

    def clean_tag(playlist_name):
        """Cleanup an spaces or unwanted characters."""
        playlist_name = "wow Sunset groove "
        fixed = "-".join(playlist_name.strip().lower().split())
        return fixed

    def add_fn(existing_tag_str, playlist_names, prefix=None, clear_existing=False):
        """
        Add a sequence of tags to an existing tag string.

        ex.
        add_fn("#my #existing", {"wow", "omg"}, prefix="$") => "#my #existing $wow $omg"
        """
        # existing_tag_str, playlist_names, prefix, clear_existing = t0.get('genre', ''), find_crates(t0['filename']), '#', clear_existing
        if not existing_tag_str or clear_existing:
            existing_tag_str = ""
        if not playlist_names:
            return existing_tag_str
        existing_tag_names = existing_tag_str.strip().split()
        tag_names = list(map(lambda pl: prefix + pl, playlist_names))
        new_field = " ".join(sorted(tag_names + existing_tag_names))
        return new_field

    def merge_tags(all_tags, playlist_tags, crate_tags, clear_existing=None):
        def lfirst(l, default=None):
            try:
                return l[0]
            except IndexError:
                return default

        find_playlists = lambda filename: lfirst(
            [
                pt
                for pt in playlist_tags
                if os.path.basename(pt["filename"]) == filename
            ],
            {},
        ).get("tags", set())
        find_crates = lambda filename: lfirst(
            [pt for pt in crate_tags if os.path.basename(pt["filename"]) == filename],
            {},
        ).get("tags", set())
        new_tags = [
            {
                **tag,
                "genre": add_fn(
                    tag.get("genre", ""),
                    find_crates(tag["filename"]),
                    prefix="#",
                    clear_existing=clear_existing,
                ),
                "comment": add_fn(
                    tag.get("comment", ""),
                    find_playlists(tag["filename"]),
                    prefix="@",
                    clear_existing=clear_existing,
                ),
            }
            for tag in all_tags
        ]
        # [ct.get('filename') for ct in crate_tags if not ct.get('filename') ]
        # t0 = all_tags[1]
        # find_crates(t0['filename'])
        # crate_tags[0]['filename'] == '/run/media/evan/5B24-5798/Mixing/Core/Tracks/GUTTA SWANGIN.mp3'
        # find_crates('/run/media/evan/5B24-5798/Mixing/Core/Tracks/GUTTA SWANGIN.mp3')
        # # find_crates(os.path.basename(t0['filename']))
        # add_fn(t0.get('genre', ''), find_crates(t0['filename']), '#', clear_existing)
        # {nt.get('genre') for nt in new_tags}
        return new_tags

    ...



# TODO
# - tests
# - write single playist/setlist at a time
# - write without clearing playlists
# - clear tags seems wonky
# - smarter tagging (clear only if not all startswith ('#'))
#   - clear tags that don't exist in playist_names

class MixxxUnused:
    """
    Once used now no longer, at least for now.
    """

    # @classmethod
    # def do_overwrite_playlist_tags(cls, track_dir, playlist_dir, existing_playlists):
    #     # Clear existing comments (in the case they're trash)
    #     print("Clearing track genre metadata")
    #     TaggerCommands.clear_metadata_dir(track_dir, "genre")
    #     # Write tags to each playist file
    #     # NOTE: this will tag all playlists, not just the ones from Mixxx
    #     for pl in existing_playlists:
    #         pl_file_name = os.path.join(playlist_dir, pl)
    #         pl_name = os.path.basename(os.path.splitext(pl_file_name)[0])
    #         pl_tag = cls.m3u_name_to_tag(pl_name, "#")
    #         print("Writing playlist tags for %s (%s)" % (pl_tag, pl_name))
    #         TaggerCommands.tag_metadata_m3u(pl_file_name, pl_tag, "genre")

    # @classmethod
    # def do_overwrite_setlist_tags(cls, track_dir, setlist_dir, existing_setlists):
    #     # Clear existing comments (in the case they're trash)
    #     print("Clearing track comment metadata")
    #     TaggerCommands.clear_metadata_dir(track_dir, "comment")
    #     # Write tags to each playist file
    #     # NOTE: this will tag all setlists, not just the ones from Mixxx
    #     for pl in existing_setlists:
    #         pl_file_name = os.path.join(setlist_dir, pl)
    #         pl_name = os.path.basename(os.path.splitext(pl_file_name)[0])
    #         pl_tag = cls.m3u_name_to_tag(pl_name, "@")
    #         print("Writing setlist tags for %s (%s)" % (pl_tag, pl_name))
    #         TaggerCommands.tag_metadata_m3u(pl_file_name, pl_tag, "comment")

    # @classmethod
    # def do_backup_dir_tags(cls, track_dir, tag_backup_dir, tag_backup_filename=None):
    #     existing_tags = TaggerCommands.read_all_tags_from_dir(track_dir)
    #     cls.backup_tags_to_dir(existing_tags, tag_backup_dir, tag_backup_filename)

    # @staticmethod
    # def backup_tags_to_dir(tags, tag_backup_dir, tag_backup_filename=None):
    #     if not tag_backup_filename:
    #         tag_backup_filename = "track-tags-backup-%s.json" % datetime.now().strftime(
    #             "%Y-%m-%dT%H-%M"
    #         )
    #     if not os.path.exists(tag_backup_dir) and os.path.isdir(tag_backup_dir):
    #         os.mkdir(tag_backup_dir)
    #     tags_backup_filepath = os.path.join(tag_backup_dir, tag_backup_filename)
    #     with open(tags_backup_filepath, "w") as backup_file:
    #         backup_file.write(json.dumps(tags))

    @classmethod
    def verify_all_playlists_exported(cls, playlist_dir, existing_playlists_names):
        all_playlists = MixxxDb.get_all_crates()
        missing_or_exess_playlists = set(all_playlists).difference(
            existing_playlists_names
        )
        if len(missing_or_exess_playlists) >= 1:
            raise Exception(
                "Failed to export playlists: %s" % str(missing_or_exess_playlists)
            )

    @classmethod
    def verify_all_setlists_exported(cls, setlist_dir, existing_setlist_names):
        all_playlists = MixxxDb.get_all_playlists()
        missing_or_exess_playlists = set(all_playlists).difference(
            existing_setlist_names
        )
        if len(missing_or_exess_playlists) >= 1:
            raise Exception(
                "Failed to export setlists: %s" % str(missing_or_exess_playlists)
            )

    @classmethod
    def do_export_all_playlists(cls, mixing_dir, tags_dir):
        in_mixing_dir = lambda path: os.path.join(mixing_dir, path)
        in_tags_dir = lambda path: os.path.join(tags_dir, path)
        cls.export_playlist(in_tags_dir("Playlists"), in_mixing_dir("Tracks"))
        cls.export_playlist(
            in_tags_dir("Relative Pathing Playlists"), "../Core/Tracks"
        )  # NOTE: useful for usbs when used cross platform (if DJ software can handle relative pathibng)
        cls.export_playlist(
            in_tags_dir("Windows Playlists"), "e:/Mixing/Core/Tracks"
        )  # FIXME: figure out correct pathing for windows

    @classmethod
    def do_export_all_setlists(cls, mixing_dir, tags_dir):
        in_mixing_dir = lambda path: os.path.join(mixing_dir, path)
        in_tags_dir = lambda path: os.path.join(tags_dir, path)
        cls.export_playlist(
            in_tags_dir("Setlists"), in_mixing_dir("Tracks"), "playlist"
        )
        cls.export_playlist(
            in_tags_dir("Relative Pathing Setlists"), "../Core/Tracks", "playlist"
        )  # NOTE: useful for usbs when used cross platform (if DJ software can handle relative pathibng)
        cls.export_playlist(
            in_tags_dir("Windows Setlists"), "D:/balh/blah", "playlist"
        )  # FIXME: figure out correct pathing for windows

    @staticmethod
    def m3u_name_to_tag(m3u_filename, prefix=None):
        if not prefix:
            prefix = "#"
        pl_name = os.path.basename(os.path.splitext(m3u_filename)[0])
        pl_lower_amp = pl_name.strip().lower().replace("&", "and")
        pl_no_funky = re.sub("[^a-zA-Z$%@!]", "-", pl_lower_amp)
        pl_multi_dash = re.sub("-+", "-", pl_no_funky)
        pl_tag = pl_multi_dash
        return "#" + pl_tag

    @staticmethod
    def export_playlist(
        playlist_dirname, overridden_track_dir=None, source_type="crate"
    ):
        """
        `overridden_track_dir` - makes the assumption that all tracks live in the same directory.
        """
        MixxxExporter.export_all_m3us(
            playlist_dirname,
            source_type,
            overwrite_existing_m3u=True,
            overridden_track_path=overridden_track_dir,
        )



MIXXX_DB_SQLITE_PATH = "/home/evan/.mixxx/mixxxdb.sqlite" # FIXME purge

class MixxxExporter:
    """
    Utils for querying mixxx-db.sqlite file
    """

    # @staticmethod
    # def export_library_as_json(database_filename, json_directory, generate_metadata_tags=False):
    #     easy_dicts = MixxxExporter.tags_from_library(database_filename)
    #     if generate_metadata_tags:
    #         # In this case we simply replace genre and comment with the crates and playlists
    #         easy_dicts = [{
    #             **ed,
    #             "genre": "".join(ed['crates']),
    #             "comment": "".join(ed["playlists"])
    #         } for ed in easy_dicts]
    #     easy_dicts = drop_keys(easy_dicts, ["id", "playlists", "crates", "location"])
    #     json_filename = os.path.join(json_directory, MixxxExporter.make_tag_backup_filename())
    #     JsonUtils.write_json_file(json_filename, easy_dicts)
    #     return json_filename

    # @staticmethod
    # def to_metadata_tags(database_filename, json_directory):
    #     easy_dicts = MixxxExporter.tags_from_library(database_filename)
    #     easy_dicts = [{
    #         **ed,
    #         "genre": "".join(ed['crates']),
    #         "comment": "".join(ed["playlists"])
    #     } for ed in easy_dicts]
    #     easy_dicts = drop_keys(easy_dicts, ["id", "playlists", "crates", "location"])
    #     return easy_dicts


    # @staticmethod
    # def make_tag_backup_filename():
    #     tag_backup_filename = "track-tags-backup-%s.json" % datetime.now().strftime(
    #         "%Y-%m-%dT%H-%M"
    #     )
    #     return tag_backup_filename

    # @classmethod
    # def export_all_m3us(
    #     cls,
    #     playlist_save_dir,
    #     source_type="crate",
    #     overwrite_existing_m3u=False,
    #     overridden_track_path=None,
    # ):
    #     """
    #     `playlist_save_dir` - directory where the m3u playlist file will be saved
    #     `track_path` - in the case of moving files, or tracks being on a usb, specify a custom one here.
    #     This is primarily useful if switching to and from windows, where the device path will likely be different.#!/usr/bin/env python
    #     Relative paths are acceptable.
    #     """
    #     if not (os.path.exists(playlist_save_dir) and os.path.isdir(playlist_save_dir)):
    #         pathlib.Path(playlist_save_dir).mkdir(parents=True, exist_ok=True)
    #     print("Exporting Playlists to: %s" % playlist_save_dir)
    #     if source_type == "playlist":
    #         playlists = MixxxDb.get_all_playlists()
    #     else:
    #         playlists = MixxxDb.get_all_crates()
    #     for pl in playlists:
    #         cls.export_m3u(
    #             pl,
    #             playlist_save_dir,
    #             source_type,
    #             overwrite_existing_m3u,
    #             overridden_track_path,
    #         )

    # @classmethod
    # def export_m3u(
    #     cls,
    #     playlist_name,
    #     playlist_save_dir,
    #     source_type="crate",
    #     overwrite_existing_m3u=False,
    #     overridden_track_path=None,
    # ):
    #     """
    #     For a given playlist_name (as listed in mixxx) for a given source_type
    #     (create or playlist), create an m3u file and save it in
    #     playlist_save_dir, optionally overwriting an existing m3u file, with the
    #     option to override the track path for each track entry in the m3u file.
    #     """
    #     m3u_name = os.path.join(playlist_save_dir, playlist_name + ".m3u")
    #     print(m3u_name)
    #     if not overwrite_existing_m3u and os.path.exists(m3u_name):
    #         raise Exception("Playlist file already exists: %s" % m3u_name)
    #     if source_type == "playlist":
    #         tracks = MixxxDb.get_all_tracks_by_playlist(playlist_name)
    #     else:
    #         tracks = MixxxDb.get_all_tracks_by_crate(playlist_name)
    #     track_filenames = [tr[1] for tr in tracks]
    #     m3u_contents = cls._make_m3u_contents(
    #         playlist_name, track_filenames, overridden_track_path
    #     )
    #     with open(m3u_name, "w") as m3u_file:
    #         m3u_file.write(m3u_contents)

    # @staticmethod
    # def _make_m3u_contents(tracks, overridden_track_path=None):
    #     if overridden_track_path:
    #         tracks = [
    #             os.path.join(overridden_track_path, os.path.basename(tr))
    #             for tr in tracks
    #         ]
    #     m3u_contents = """#EXTM3U\n"""
    #     for tr in tracks:
    #         m3u_contents += "#EXTINF\n%s\n" % tr
    #     return m3u_contents



#     @classmethod
#     def get_all_crates(cls):
#         return [c[0] for c in cls.query_mixxx("select name from crates;")]

#     @classmethod
#     def get_all_playlists(cls):
#         """
#         All Playlists that are not `Auto DJ` or just random session set lists. (only hand crafted playlists)
#         """
#         return [
#             c[0]
#             for c in cls.query_mixxx(
#                 "select name from Playlists pl where pl.name not like '202%' and pl.name != 'Auto DJ';"
#             )
#         ]

#     @classmethod
#     def get_all_tracks_by_crate(cls, crate):
#         return cls.query_mixxx(
#             """
#     select cr.name, tl.location from crates cr
#     join crate_tracks ct on cr.id = ct.crate_id
#     left join library l on l.id = ct.track_id
#     left join track_locations tl on tl.id = l.location
#     where cr.name = ?
#     order by cr.name
#         """,
#             (crate,),
#         )

#     @classmethod
#     def get_all_tracks_by_playlist(cls, playlist):
#         return cls.query_mixxx(
#             """
#     select pl.name, tl.location, pt.position from Playlists pl
#     join PlaylistTracks pt on pl.id = pt.playlist_id
#     left join library l on l.id = pt.track_id
#     left join track_locations tl on tl.id = l.location
#     where pl.name = ?
#     order by pl.name, pt.position
#         """,
#             (playlist,),
#         )

#     @classmethod
#     def get_all_tracks_grouped_by_crates(cls):
#         return cls.query_mixxx(
#             """
#     select cr.name, tl.location from crates cr
#     left join crate_tracks ct on cr.id = ct.crate_id
#     left join library l on l.id = ct.track_id
#     left join track_locations tl on tl.id = l.location
#     order by cr.name
#         """
#         )

#     @classmethod
#     def get_all_tracks_grouped_by_playlists(cls):
#         return cls.query_mixxx(
#             """
# select pl.name, tl.location, pt.position from Playlists pl
# left join PlaylistTracks pt on pl.id = pt.playlist_id
# left join library l on l.id = pt.track_id
# left join track_locations tl on tl.id = l.location
# where pl.name not like '202%' and pl.name != 'Auto DJ'
# order by pl.name, pt.position;
#         """
#         )

    # @classmethod
    # def query_mixxx(cls, query, *args):
    #     return cls.query_db(MIXXX_DB_SQLITE_PATH, query, *args)


class UnusedFileUtils:

    @staticmethod
    def add_metadata_to_files(filenames, tag_name, metadata_name, remove_tags=False):
        easy_dicts = EasyFileUtils.read_tags_from_filenames(filenames)
        MetaDataTagUtils.add_metadata_tags(
            easy_dicts, tag_name, metadata_name, remove_tags
        )
        EasyFileUtils.write_tags_to_files(easy_dicts)

    @staticmethod
    def clear_metadata_from_files(filenames, metadata_name):
        """Clear all the comment tags for tracks in a given directory"""
        easy_dicts = EasyFileUtils.read_tags_from_filenames(filenames)
        MetaDataTagUtils.clear_all_specified_metadata(easy_dicts, metadata_name)
        EasyFileUtils.write_tags_to_files(easy_dicts)
