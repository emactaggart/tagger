import os
from tagger.utils import drop_keys
from tagger.core import EasyFileUtils
from tagger import serato, serato_tags_scripts_database_v2
from tests.test_cmd import resource
from unittest.case import TestCase


serato_directory = resource("_Serato_")


class SeratoTests(TestCase):
    def test_serato_get_library(self):
        tags = serato.tags_from_library(serato_directory)
        assert drop_keys(tags, []) == [
            {
                "playlists": [],
                "crates": ["!abc", "#def", "hig"],
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
                "crates": ["!abc", "#def", "hig"],
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
                "crates": ["!abc", "#def", "hig"],
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
                "crates": ["!abc", "#def", "hig", "#dnb"],
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
        ]
