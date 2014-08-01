from onionshare.hidden_service import *
import socket
import stem
import unittest

class MockSubprocess:
  def __init__(self):
      self.last_call = None

  def call(self, args):
      self.last_call = args

  def last_call_args(self):
      return self.last_call

class MockController:

    return_none = False

    @classmethod
    def from_port(self, port):
        if self.return_none:
            return None
        else:
            return MockController()

    def set_options(self, args):
        self.options = args

    def get_options(self):
        return self.options

    def authenticate(self):
        self.authenticated = True

class HiddenServiceTests(unittest.TestCase):

    def test_set_up_hidden_service(self):
        "HiddenService.set_up_hidden_service sets the correct options on the controller"
        service = HiddenService.build()
        service.controller = MockController()
        service.hidden_service_directory = 'directory'
        service.port = 'port'
        service._set_up_hidden_service()
        options = service.controller.get_options()
        assert options == [('HiddenServiceDir', 'directory'), ('HiddenServicePort', '80 127.0.0.1:port')]

    def test_generate_hidden_service_directory(self):
        "HiddenService.generate_hidden_service_directory generates a directory name for a non-Windows directory"
        os.urandom = lambda x: '12345678'
        random_to_hex = ('12345678').encode('hex')
        service = HiddenService.build()
        service._generate_hidden_service_directory()
        assert service.hidden_service_directory == "/tmp/onionshare_{0}".format(random_to_hex)

    def test_generate_hidden_service_directory_windows(self):
        "HiddenService.generate_hidden_service_directory generates a directory name for a Windows directory"
        platform.system = lambda: 'Windows'
        os.urandom = lambda x: '12345678'
        random_to_hex = ('12345678').encode('hex')
        service = HiddenService.build()
        service._generate_hidden_service_directory()
        assert service.hidden_service_directory == "C:/tmp/onionshare_{0}".format(random_to_hex)

    def test_generate_hidden_service_directory_windows(self):
        "HiddenService.generate_hidden_service_directory generates a directory name for a Windows directory when Temp is set"
        platform.system = lambda: 'Windows'
        os.urandom = lambda x: '12345678'
        os.environ['Temp'] = 'F:\\crazy\windows\path'
        random_to_hex = ('12345678').encode('hex')
        service = HiddenService.build()
        service._generate_hidden_service_directory()
        assert service.hidden_service_directory == "F:/crazy/windows/path/onionshare_{0}".format(random_to_hex)

    def test_try_controlport(self):
        "HiddenService._try_controlport() returns a controller when it does not throw an error"
        service = HiddenService.build()
        stem.control.Controller = MockController
        service._try_controlport(9051)
        assert type(service.controller) == MockController

    def test_try_controlport(self):
        "HiddenService._try_controlport() returns None when it throws an error"
        service = HiddenService.build()
        service._try_controlport(9051)
        assert service.controller == None

    def test_hidden_service_returns_local_service(self):
        "HiddenService.build() returns a local service when the local_only flag is True"
        local_service = HiddenService.build(True)
        assert isinstance(local_service, HiddenService)
        assert type(local_service) == LocalService

    def test_hidden_service_returns_hidden_service(self):
        "HiddenService.build() returns a hidden service by default"
        hidden_service = HiddenService.build()
        assert type(hidden_service) == HiddenService

    def test_hidden_service_returns_tails_service(self):
        "HiddenService.build() returns a Tails service when the platform is Tails"
        platform.system = lambda: 'Tails'
        platform.uname = lambda: ('Linux', 'amnesia')
        os.geteuid = lambda: 0

        tails_service = HiddenService.build()
        assert isinstance(tails_service, HiddenService)
        assert type(tails_service) == TailsService

    def test_choose_port_returns_a_port_number(self):
        "choose_port() returns a port number"
        port = choose_open_port()
        assert  1024 <= port <= 65535

    def test_choose_port_returns_an_open_port(self):
        "choose_port() returns an open port"
        port = choose_open_port()
        socket.socket().bind(("127.0.0.1", port))

    def test_get_platform_on_tails(self):
        "get_platform() returns 'Tails' when hostname is 'amnesia'"
        platform.uname = lambda: ('Linux', 'amnesia', '3.14-1-amd64', '#1 SMP Debian 3.14.4-1 (2014-05-13)', 'x86_64', '')
        assert get_platform() == 'Tails'

    def test_get_platform_returns_platform_system(self):
        "get_platform() returns platform.system()"
        platform.system = lambda: 'Sega Saturn'
        assert get_platform() == 'Sega Saturn'

    def test_is_root_with_uid_zero(self):
        "is_root returns True for uid 0"
        os.geteuid = lambda: 0
        assert is_root()

    def test_is_not_root_with_other_uids(self):
        "is_root returns False for other uids"
        os.geteuid = lambda: 1
        assert is_root() == False

    def test_tails_open_port(self):
        "tails_open_port() calls iptables with ACCEPT arg"
        os.geteuid = lambda: 0
        platform.system = lambda: 'Tails'

        mock_subprocess = MockSubprocess()
        subprocess.call = mock_subprocess.call

        service = TailsService()
        service.start()

        expected_call = [
            '/sbin/iptables', '-I', 'OUTPUT',
            '-o', 'lo', '-p',
            'tcp', '--dport', str(service.port), '-j', 'ACCEPT'
            ]
        actual_call = mock_subprocess.last_call_args()
        assert actual_call == expected_call

    def test_tails_close_port(self):
        "tails_close_port() calls iptables with REJECT arg"
        platform.system = lambda: 'Tails'
        os.geteuid = lambda: 0

        mock_subprocess = MockSubprocess()
        subprocess.call = mock_subprocess.call
        service = TailsService()
        service.shutdown()

        expected_call = [
            '/sbin/iptables', '-I', 'OUTPUT',
            '-o', 'lo', '-p',
            'tcp', '--dport', str(service.port), '-j', 'REJECT'
            ]
        actual_call = mock_subprocess.last_call_args()
        assert actual_call == expected_call

    def test_local_service_sets_localhost_as_host(self):
        "LocalService sets 127.0.0.1 as its host"
        service = HiddenService.build(True)
        service.port = 'port'
        service.start()
        assert service.host == '127.0.0.1:port'

    def test_connecting_to_tor_controlport_creates_controller(self):
        "Connecting to the tor controlport creates a controller if one is not defined"
        service = HiddenService.build()
        stem.control.Controller = MockController
        service._connect_to_tor_controlport()
        assert isinstance(service.controller, MockController)

    def test_failed_connection_to_tor_controlport_exits(self):
        service = HiddenService.build()
        MockController.return_none = True
        stem.control.Controller = MockController()
        self.assertRaises(SystemExit, service._connect_to_tor_controlport)

    def test_connecting_to_tor_controlport_authenticates(self):
        "Connecting to the tor controlport calls authenticate()"
        service = HiddenService.build()
        service.controller = MockController()
        service._connect_to_tor_controlport()
        assert service.controller.authenticated




