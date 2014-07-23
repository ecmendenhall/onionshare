import Queue

class RequestQueue:

  REQUEST_LOAD = 0
  REQUEST_DOWNLOAD = 1
  REQUEST_PROGRESS = 2
  REQUEST_OTHER = 3

  def __init__(self):
      self.q = Queue.Queue()

  def add_request(self, type, path, data=None):
      self.q.put({
        'type': type,
        'path': path,
        'data': data
      })
