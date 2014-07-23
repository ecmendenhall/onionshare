from onionshare.shared_file import *
import tempfile
import unittest

def write_tempfile(text):
    tempdir = tempfile.mkdtemp()
    path = tempdir + "/test-file.txt"
    with open(path, "w") as f:
      f.write(text)
      f.close()
    return path

def make_file():
    text = """
           If you want a picture of the future, imagine a boot stamping on an
           encrypted, redundant, distributed filesystem -- forever.
           """
    tempfile = write_tempfile(text)
    return SharedFile(tempfile)

def is_hex(string):
    hex_alphabet = "01234556789abcdef"
    return all(char in hex_alphabet for char in string)

class SharedFileTests(unittest.TestCase):

    def test_generate_slug_length(self):
        "generates a 32-character slug"
        shared_file = make_file()
        assert len(shared_file.slug) == 32

    def test_generate_slug_characters(self):
        "generates a hex slug"
        shared_file = make_file()
        assert is_hex(shared_file.slug)

    def test_filehash_returns_correct_hash(self):
        "calculates correct hash"
        shared_file = make_file()
        assert shared_file.filehash == 'bc004fe72e6530a545570b4c6ce76bcb78ea526b'

    def test_filesize_returns_correct_size(self):
        "calculates correct file size"
        shared_file = make_file()
        assert shared_file.filesize == 158

    def test_basename_returns_correct_name(self):
        "basename returns correct name"
        shared_file = make_file()
        assert shared_file.basename == 'test-file.txt'

    def test_raises_error_if_file_not_found(self):
        "raises an error if the file is not found"
        os.path.isfile = lambda f: False
        self.assertRaises(NoFile, make_file)
