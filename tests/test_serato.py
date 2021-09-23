import os
from tagger import serato, serato_tags_scripts_database_v2
from tests.test_cmd import resource
from unittest.case import TestCase

serato_directory = resource("_Serato_")

# serato_full = "/home/evan/Development/tagger/tests/resources/TaggerFiles/_Serato_full"
# serato_true = "/home/evan/Development/tagger/tests/resources/TaggerFiles/_Serato_"
# serato_local = "/home/evan/Development/tagger/tests/resources/TaggerFiles/_Serato_local"
# serato_local_big = (
#     "/home/evan/Development/tagger/tests/resources/TaggerFiles/_Serato_local_big"
# )
# serato_remote_big = (
#     "/home/evan/Development/tagger/tests/resources/TaggerFiles/_Serato_remote_big"
# )


serato_directory = resource("_Serato_")


def wow():
    tags = serato.tags_from_library(serato_directory)

    assert drop_keys(tags, []) == [
        {
            "playlists": [],
            "crates": [],
            "filename": "test.mp3",
            "title": "title",
            "artist": "artist",
            "album": "album",
            "genre": "#g2 #genre",
            "comment": "@comment",
            "_filename": "/tagger/tests/resources/test.mp3",
        },
        {
            "playlists": [],
            "crates": [],
            "filename": "test.m4a",
            "title": "title",
            "artist": "artist",
            "album": "album",
            "genre": "#g2 #genre",
            "comment": "@comment",
            "_filename": "/tagger/tests/resources/test.m4a",
        },
        {
            "playlists": [],
            "crates": [],
            "filename": "test.flac",
            "title": "title",
            "artist": "artist",
            "album": "album",
            "genre": "#g2 #genre",
            "comment": "@comment",
            "_filename": "/tagger/tests/resources/test.flac",
        },
        {
            "playlists": [],
            "crates": [],
            "filename": "error.wav",
            "title": "title",
            "artist": "artist",
            "album": "album",
            "genre": "#genre",
            "comment": "@comment",
            "_filename": "/tagger/tests/resources/error.wav",
        },
        {
            "playlists": [],
            "crates": [],
            "filename": "error.aiff",
            "title": "error",
            "_filename": "/tagger/tests/resources/error.aiff",
        },
        {
            "playlists": [],
            "crates": [],
            "filename": "flavour-town.mp3",
            "title": "title",
            "artist": "artist",
            "album": "album",
            "genre": "#g2 #genre",
            "comment": "@comment",
            "_filename": "/tagger/tests/resources/flavour-town.mp3",
        },
    ]
