import hashlib, os

class NoFile:
    pass

class SharedFile(object):

  def __init__(self, filename):
      if not (filename and os.path.isfile(filename)):
          raise NoFile

      self.filename = filename
      self.basename = os.path.basename(filename)
      self.dirname  = os.path.dirname(filename)
      self.filesize = os.path.getsize(filename)
      self.filehash = self.__hash(filename)
      self.slug     = os.urandom(16).encode('hex')

  def __hash(self, filename):
      BLOCKSIZE = 65536
      hasher = hashlib.sha1()
      with open(filename, 'rb') as f:
          buf = f.read(BLOCKSIZE)
          while len(buf) > 0:
              hasher.update(buf)
              buf = f.read(BLOCKSIZE)
      return hasher.hexdigest()
