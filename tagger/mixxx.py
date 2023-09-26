import os
import sqlite3
from tagger.utils import absolute_path



def rename_track_locations(database_filename, original, replacement):
    """
    ie, the location, filename, and directory in the `track_locations` table
    """
    rename_query = """
update track_locations
set location = :to,
    filename = :to_filename,
    directory = :to_directory
where location = :from
        """
    _query_db(
        database_filename,
        rename_query,
        {
            "from": original,
            "to": replacement,
            "to_filename": os.path.basename(replacement),
            "to_directory": os.path.dirname(replacement),
        },
    )


def nuke_invalid_metadata(database_filename, filename):
    """
    Mixxx does not allow you to reimport bitrate form metadata if it already
    exists, so we must nuke it in the case where it may have changed behind the
    scenes.
    """
    # for testing
    # json_filename = "~/Music/Mixing/Util/new-songs.json"
    # library_path = "~/.mixxx/mixxxdb.sqlite"
    # replacements, invalid = parse_replacements(
    #     replacement_dicts=EasyFileUtils.read_json_file(json_filename)
    # )
    # for filename_from, filename_to in replacements:
    #     # mixxx.rename_track_locations(absolute_path(library_path), filename_from, filename_to)
    #     print(filename_to)
    #     mixxx.nuke_invalid_metadata(absolute_path(library_path), filename_to)
    #     # mixxx.nuke_bitrate(database_filename=absolute_path(library_path), filename="/run/media/evan/5B24-5798/Mixing/Core/Tracks/1-01 Cold Spring.flac")

    nuke_query = """
update library
set bitrate = Null,
    duration = Null
where location = (select id from track_locations where location = :location limit 1)
        """
    _query_db(
        database_filename,
        nuke_query,
        {
            "location": filename,
        }
    )


def tags_from_library(database_filename):
    """
    Fetch a reasonably formatted list of metadata_tag dicts
    """
    lib = _query_for_library(database_filename)
    split_comma = lambda string: sorted(string.split(",")) if string else ""
    easy_dicts = [
        {
            **track,
            "filename": os.path.basename(track.get("location")),
            "_filename": track.get("location"),
            "playlists": split_comma(track.get("playlists")),
            "crates": split_comma(track.get("crates")),
            "genre": track["genre"] or "",
            "comment": track["comment"] or "",
        }
        for track in lib
    ]
    return easy_dicts


def _query_for_library(database_filename):
    return list(
        map(
            dict,
            _query_db(
                database_filename,
                """
select
    l.id,
    tl.location,
    l.title,
    l.artist,
    l.album,
    l.genre,
    l.comment,
    (select group_concat(replace(pl.name, " ", "-"), ",") from Playlists pl
            join PlaylistTracks pt on pl.id = pt.playlist_id
            where l.id = pt.track_id
                  and pl.name not like '202%' and pl.name != 'Auto DJ'
            order by pl.name
    ) as playlists,
    (select group_concat(replace(cr.name, " ", "-"), ",") from Crates cr
            join crate_tracks ct on cr.id = ct.crate_id
            where l.id = ct.track_id
            order by cr.name
    ) as crates
from library l
join track_locations tl on tl.id = l.location
""", []
            ),
        )
    )


def _query_db(db, query, args):
    with sqlite3.connect(absolute_path(db)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        results = cursor.fetchall()
    return results
