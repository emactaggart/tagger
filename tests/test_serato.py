
import os
from tagger import serato
from tests.test_cmd import resource_dir
from unittest.case import TestCase

serato_directory = os.path.join(resource_dir, "_Serato_")

class SeratoTests(TestCase):

    def test_tags_from_library(self):

        # serato.tags_from_library(serato_directory)
        ...

    ...
