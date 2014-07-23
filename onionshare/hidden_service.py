import os, platform, socket, subprocess, sys
import stem
from stem.control import Controller
from stem import SocketError
from strings import Strings

def get_platform():
    system = platform.system()
    return 'Tails' if is_tails(system) else system

def is_root():
    return os.geteuid() == 0

def is_tails(system):
    return system == 'Linux' and platform.uname()[0:2] == ('Linux', 'amnesia')

def choose_open_port():
    # let the OS choose a port
    tmpsock = socket.socket()
    tmpsock.bind(("127.0.0.1", 0))
    port = tmpsock.getsockname()[1]
    tmpsock.close()
    return port

class HiddenService(object):

  @classmethod
  def build(self, local_only=False):
      if local_only:
          return LocalService()
      elif get_platform() == 'Tails':
          return TailsService()
      else:
          return HiddenService()

  def __init__(self):
    self.strings = Strings()
    self.port = choose_open_port()
    self.controller = None

  def start(self):
      self._start_hidden_service()

  def shutdown(self):
      pass

  def _start_hidden_service(self):
      self._generate_hidden_service_directory()
      self._connect_to_tor_controlport()
      self._set_up_hidden_service()
      onion_host = self._get_hostname()
      self.host = onion_host

  def _generate_hidden_service_directory(self):
      hidserv_dir_rand = os.urandom(8).encode('hex')
      if get_platform() == "Windows":
          temp = self._get_windows_temp_directory()
          self.hidden_service_directory = "{0}/onionshare_{1}".format(temp, hidserv_dir_rand)
      else:
          self.hidden_service_directory = "/tmp/onionshare_{0}".format(hidserv_dir_rand)

  def _get_windows_temp_directory(self):
      return os.environ['Temp'].replace('\\', '/') if 'Temp' in os.environ else 'C:/tmp'

  def _try_controlport(self, controlport):
      try:
          return stem.control.Controller.from_port(port=controlport)
      except SocketError:
          pass

  def _connect_to_tor_controlport(self):
      controlports = [9051, 9151]
      print self.strings.get("connecting_ctrlport").format(self.port)
      for controlport in controlports:
          if not self.controller:
              self.controller = self._try_controlport(controlport)
      if not self.controller:
          sys.exit(self.strings.get("cant_connect_ctrlport").format(controlports))
      self.controller.authenticate()

  def _set_up_hidden_service(self):
      self.controller.set_options([
          ('HiddenServiceDir', self.hidden_service_directory),
          ('HiddenServicePort', '80 127.0.0.1:{0}'.format(self.port))
      ])

  def _get_hostname(self):
      hostname_file = '{0}/hostname'.format(self.hidden_service_directory)
      return open(hostname_file, 'r').read().strip()

class LocalService(HiddenService):
    def start(self):
        self.host = "127.0.0.1:{0}".format(self.port)

class TailsService(HiddenService):
  def __init__(self):
    self.strings = Strings()

    if get_platform() == 'Tails' and not is_root():
        sys.exit(self.strings.get("tails_requires_root"))

    self.port = choose_open_port()

  def start(self):
      self.tails_open_port()
      super

  def shutdown(self):
      self.tails_close_port()

  def tails_open_port(self):
      if get_platform() == 'Tails':
          print self.strings.get("punching_a_hole")
          subprocess.call(['/sbin/iptables', '-I', 'OUTPUT', '-o', 'lo', '-p', 'tcp', '--dport', str(self.port), '-j', 'ACCEPT'])

  def tails_close_port(self):
      if get_platform() == 'Tails':
          print self.strings.get("closing_hole")
          subprocess.call(['/sbin/iptables', '-I', 'OUTPUT', '-o', 'lo', '-p', 'tcp', '--dport', str(self.port), '-j', 'REJECT'])
