import os
import sqlite3
from tagger.utils import absolute_path


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
    (select group_concat("@" || replace(pl.name, " ", "-"), ",") from Playlists pl
            join PlaylistTracks pt on pl.id = pt.playlist_id
            where l.id = pt.track_id
                  and pl.name not like '202%' and pl.name != 'Auto DJ'
            order by pl.name
    ) as playlists,
    (select group_concat("#" || replace(cr.name, " ", "-"), ",") from Crates cr
            join crate_tracks ct on cr.id = ct.crate_id
            where l.id = ct.track_id
            order by cr.name
    ) as crates
from library l
join track_locations tl on tl.id = l.location
""",
            ),
        )
    )


def _query_db(db, query, *args):
    with sqlite3.connect(absolute_path(db)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, *args)
        results = cursor.fetchall()
    return results
