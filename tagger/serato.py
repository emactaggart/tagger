import os
from tagger.utils import absolute_path, first
from tagger.serato_tags_scripts_database_v2 import parse


def tags_from_library(serato_directory):
    """
    # FIXME cross device tracks? Since serato doesn't have a full filepath
    """

    all_tracks = _database_v2_contents(serato_directory)
    all_crates = _all_crates(serato_directory)
    find_track = lambda fn: first([tr for tr in all_tracks if tr["filename"] == fn])

    missing_from_lib = []  # not from playlists (unlikely to ever happen)
    for crate in all_crates:
        for track_name in crate[1]:
            track_details = find_track(track_name)
            if track_details:
                track_details["crates"] = track_details.get("crates", [])
                if not "crates" in track_details:
                    track_details["crates"] = []
                track_details["crates"].append(crate[0])
                print(track_details)
            else:
                missing.append(track_name)

    all_tracks = [
        {
            "playlists": [],
            "crates": [],
            **track,
            "_filename": os.path.join(serato_directory, track["filename"]),
            "filename": os.path.basename(track["filename"]),
        }
        for track in all_tracks
    ]
    return all_tracks


def _all_crates(serato_directory):
    crate_dir = os.path.join(serato_directory, "Subcrates")
    crate_filenames = os.listdir(crate_dir)
    crates = []
    for crate_name in crate_filenames:
        crate_contents = None
        with open(os.path.join(crate_dir, crate_name), "rb") as crate_file:
            crate_contents = list(parse(crate_file))
        new_name = crate_name[: -len(".crate")].replace("%%", "/")
        crates.append((new_name, _parse_crate(crate_contents)))
    return crates


def _parse_crate(crate_contents):
    len(crate_contents)
    tracks = [line for line in crate_contents if line[0] == "otrk"]
    header_index = 0
    value_index = 2
    magic_index_b = 0
    path_index = 2
    track_header = "otrk"
    filenames = [
        line[value_index][magic_index_b][path_index]
        for line in crate_contents
        if line[header_index] == track_header
    ]
    return filenames


def _database_v2_contents(serato_directory):
    db_path = os.path.join(absolute_path(serato_directory), "database V2")
    with open(db_path, "rb") as db:
        db_contents = list(parse(db))
    return _parse_lib(db_contents)


def _parse_lib(db_contents):
    column_names = {
        "pfil": "filename",
        "tsng": "title",
        "tart": "artist",
        "tgen": "genre",
        "tcom": "comment",
        "talb": "album",
    }

    def track_tuple_to_dict(tup):
        track = {}
        for col in tup:
            if col[0] in column_names.keys():
                track[column_names[col[0]]] = col[2]
        return track

    raw_tracks = [line[2] for line in db_contents if line[0] == "otrk"]
    tracks = [track_tuple_to_dict(track) for track in raw_tracks]
    return tracks
