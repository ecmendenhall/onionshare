from onionshare.file_server import *
from onionshare.shared_file import SharedFile
from onionshare.request_queue import RequestQueue
import tempfile, unittest

def write_tempfile(text):
    tempdir = tempfile.mkdtemp()
    path = tempdir + "/test-file.txt"
    with open(path, "w") as f:
      f.write(text)
      f.close()
    return path

def make_file(text):
    tempfile = write_tempfile(text)
    return SharedFile(tempfile)

class FileServerTest(unittest.TestCase):

    def setUp(self):
        self.text = """
        If you want a picture of the future, imagine a boot stamping on an
        encrypted, redundant, distributed filesystem -- forever.
        """
        self.test_file = make_file(self.text)
        self.queue = RequestQueue()
        self.server = FileServer.build(self.test_file, self.queue)
        self.app = self.server.test_client()

    def test_visiting_unknown_route_enqueues_event(self):
        "visiting an unregistered route enqueues a type 3 event."
        self.app.get('/')
        event = self.queue.q.get(False)
        assert event == {'data': None, 'path': '/', 'type': 3}

    def test_visiting_slug_route_enqueues_event(self):
        "visiting a file route enqueues a type 0 event."
        slug_route = "/{0}".format(self.test_file.slug)
        self.app.get(slug_route)
        event = self.queue.q.get(False)
        assert event == {'data': None, 'path': slug_route, 'type': 0}

    def test_visiting_download_route_enqueues_event(self):
        "visiting a file download route enqueues a type 1 event."
        download_route = "/{0}/download".format(self.test_file.slug)
        self.app.get(download_route)
        event = self.queue.q.get(False)
        assert event == {'data': {'id': 0}, 'path': download_route, 'type': 1}

    def test_visiting_download_route_twice_increments_id(self):
        "visiting a download route more than once increments the id."
        download_route = "/{0}/download".format(self.test_file.slug)
        self.app.get(download_route)
        self.app.get(download_route)
        self.queue.q.get(False)
        event = self.queue.q.get(False)
        assert event == {'data': {'id': 1}, 'path': download_route, 'type': 1}

    def test_visiting_download_route_downloads_file(self):
        "visiting a download route more than once increments the id."
        download_route = "/{0}/download".format(self.test_file.slug)
        response = self.app.get(download_route)
        assert response.data == self.text

    def test_downloading_file_returns_correct_content_length(self):
        "file download adds correct Content-Length header"
        download_route = "/{0}/download".format(self.test_file.slug)
        response = self.app.get(download_route)
        assert response.headers['Content-Length'] == str(self.test_file.filesize)

    def test_downloading_file_returns_correct_content_disposition(self):
        "file download adds correct Content-Length header"
        download_route = "/{0}/download".format(self.test_file.slug)
        response = self.app.get(download_route)
        assert response.headers['Content-Disposition'] == 'attachment; filename=test-file.txt'
