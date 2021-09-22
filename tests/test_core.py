from tagger.core import AUDIO_FILE_METADATA_FIELDS
from tagger.core import EasyFileUtils
from unittest import TestCase

from tagger.core import MetaDataTagUtils


class MetaDataTagUtilsTests(TestCase):
    def test_add_metadata_tags__udpates_dicts_with_new_tags(self):
        easy_dicts = [{"title": "wow", "genre": "1234"}, {"genre": "a"}, {}]
        tag_name = "#asdf"
        metadata_fields = ["genre"]
        MetaDataTagUtils.add_metadata_tags(
            easy_dicts, tag_name, metadata_fields, remove_tag=False
        )
        assert easy_dicts == [
            {"title": "wow", "genre": "#asdf 1234"},
            {"genre": "#asdf a"},
            {"genre": "#asdf"},
        ]

    def test_clear_all_specified_metadata__removes_specified_metadata_fields_successfully(
        self,
    ):
        easy_dicts = [
            {"title": "wow", "def": "wow", "artist": "wow"},
            {"title": None, "def": "wow"},
            {"def": "wow"},
        ]
        metadata_fields = ["title", "artist"]
        MetaDataTagUtils.clear_all_specified_metadata(easy_dicts, metadata_fields)
        assert easy_dicts == [
            {"title": "", "def": "wow", "artist": ""},
            {"title": "", "def": "wow", "artist": ""},
            {"def": "wow", "title": "", "artist": ""},
        ]

    def test_clear_all_specified_metadata__with_invalid_field__fails_loudly(self):
        metadata_fields = ["bpm"]
        try:
            MetaDataTagUtils.clear_all_specified_metadata([], metadata_fields)
        except ValueError:
            ...

    def test_validate_metadata_fields__with_valid_fields__passes(self):
        metadata_fields = ["artist", "title"]
        MetaDataTagUtils.validate_metadata_fields(metadata_fields)

    def test_validate_metadata_fields__with_invalid_fields__fails_loudly(self):
        metadata_fields = ["wow"]
        try:
            MetaDataTagUtils.validate_metadata_fields(metadata_fields)
        except ValueError:
            ...

    def test_add_tag_fn__adds_tag_successfully(self):
        metadata = "#jazz"
        tag_to_add = "#dank"
        result = MetaDataTagUtils.add_tag_fn(metadata, tag_to_add)
        assert result == "#dank #jazz"

    def test_add_tag_fn__with_preexisting_tag__does_not_add_duplicates(self):
        metadata = "#dank #jazz"
        tag_to_add = "#jazz"
        result = MetaDataTagUtils.add_tag_fn(metadata, tag_to_add)
        assert result == "#dank #jazz"

    def test_add_tag_fn__with_blank_metadata__creates_singleton_tag(self):
        metadata = None
        tag_to_add = "#jazz"
        result = MetaDataTagUtils.add_tag_fn(metadata, tag_to_add)
        assert result == "#jazz"

    def test_remove_tag_fn__happy_path(self):
        metadata = "#dnb #bass #pop"
        tag_to_rm = "#pop"
        result = MetaDataTagUtils.remove_tag_fn(metadata, tag_to_rm)
        assert result == "#bass #dnb"

    def test_remove_tag_fn__tag_to_rm_does_not_exist__metadata_remains_unchanged(self):
        metadata = "#dnb #bass #pop"
        tag_to_rm = "pop"
        result = MetaDataTagUtils.remove_tag_fn(metadata, tag_to_rm)
        assert result == "#bass #dnb #pop"
