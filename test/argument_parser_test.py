from onionshare.argument_parser import *
import os, sys, unittest

class ArgumentParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = ArgumentParser()
        sys.argv = ['onionshare', 'secrets.pdf']

    def test_argument_parser_returns_filename(self):
        "parses absolute filepath from args"
        filename, _ = self.parser.parse()
        assert filename == os.path.abspath('secrets.pdf')

    def test_argument_parser_returns_local_only(self):
        "parses local only flag from args"
        sys.argv = ['onionshare', 'secrets.pdf', '--local-only']
        _, local_only = self.parser.parse()
        assert local_only

    def test_argument_parser_defaults_local_only_to_false(self):
        "sets local only flag false by default"
        _, local_only = self.parser.parse()
        assert local_only == False
