from onionshare_gui.webapp import *
from onionshare.hidden_service import HiddenService
from onionshare.shared_file import SharedFile
from onionshare_gui.onionshare_gui import Application
import json, tempfile, unittest

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

class MockThread:

    instance = None

    @classmethod
    def last_instance(self):
        return self.instance

    def __init__(self, target, kwargs):
        self.target = target
        self.kwargs = kwargs
        MockThread.instance = self

    def start(self):
        self.started = True

class WebAppTest(unittest.TestCase):

    def setUp(self):
        self.text = """
        If you want a picture of the future, imagine a boot stamping on an
        encrypted, redundant, distributed filesystem -- forever.
        """
        self.test_file = make_file(self.text)
        self.hidden_service = HiddenService.build(True)
        self.hidden_service.start()
        self.qtapp = Application()
        self.app = WebApp.build(self.hidden_service, self.test_file, self.qtapp).test_client()

    def test_init_info_returns_basename(self):
        "GET /init_info returns file basename as JSON"
        response = self.app.get('/init_info')
        response_dict = json.loads(response.data)
        assert response_dict['basename'] == 'test-file.txt'

    def test_init_info_returns_strings(self):
        "GET /init_info returns file basename as JSON"
        response = self.app.get('/init_info')
        response_dict = json.loads(response.data)
        assert response_dict['strings'] == Strings().strings

    def test_start_onionshare_starts_service(self):
        "GET /start_onionshare starts the service in a new thread"
        threading.Thread = MockThread
        response = self.app.get('/start_onionshare')
        thread = MockThread.last_instance()
        assert thread.started
        assert thread.daemon
        assert thread.kwargs == {'port': self.hidden_service.port}

    def test_start_onionshare_returns_filehash(self):
        "GET /start_onionshare returns file hash as JSON"
        threading.Thread = MockThread
        response = self.app.get('/start_onionshare')
        response_dict = json.loads(response.data)
        assert response_dict['filehash'] == self.test_file.filehash

    def test_start_onionshare_returns_filesize(self):
        "GET /start_onionshare returns file size as JSON"
        threading.Thread = MockThread
        response = self.app.get('/start_onionshare')
        response_dict = json.loads(response.data)
        assert response_dict['filesize'] == self.test_file.filesize

    def test_start_onionshare_returns_url(self):
        "GET /start_onionshare returns url as JSON"
        threading.Thread = MockThread
        response = self.app.get('/start_onionshare')
        response_dict = json.loads(response.data)
        url = 'http://{0}/{1}'.format(self.hidden_service.host, self.test_file.slug)
        assert response_dict['url'] == url
