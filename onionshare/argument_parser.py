import argparse, os

class ArgumentParser(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('--local-only', action='store_true', dest='local_only', help='Do not attempt to use tor: for development only')
    self.parser.add_argument('filename', nargs=1)

  def parse(self):
    args = self.parser.parse_args()
    return self._filename(args), self._local_only_flag(args)

  def _filename(self, args):
      return os.path.abspath(args.filename[0])

  def _local_only_flag(self, args):
      return args.local_only

