import onionshare, webapp
import os, sys, subprocess, inspect

from onionshare.shared_file import SharedFile
from onionshare.hidden_service import get_platform, is_root
from webapp import WebApp
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

window_icon = None

class Application(QApplication):
    def __init__(self):
        platform = get_platform()
        if platform == 'Tails' or platform == 'Linux':
            self.setAttribute(Qt.AA_X11InitThreads, True)

        QApplication.__init__(self, sys.argv)

class WebAppThread(QThread):
    def __init__(self, wbapp, webapp_port):
        QThread.__init__(self)
        self.wbapp = wbapp
        self.webapp_port = webapp_port

    def run(self):
        self.wbapp.run(port=self.webapp_port)

class Window(QWebView):
    def __init__(self, basename, webapp_port):
        global window_icon
        QWebView.__init__(self)
        self.setWindowTitle("{0} | OnionShare".format(basename))
        self.resize(580, 400)
        self.setMinimumSize(580, 400)
        self.setMaximumSize(580, 400)
        self.setWindowIcon(window_icon)
        self.load(QUrl("http://127.0.0.1:{0}".format(webapp_port)))

def alert(msg, icon=QMessageBox.NoIcon):
    global window_icon
    dialog = QMessageBox()
    dialog.setWindowTitle("OnionShare")
    dialog.setWindowIcon(window_icon)
    dialog.setText(msg)
    dialog.setIcon(icon)
    dialog.exec_()

def select_file(strings):
    # get filename, either from argument or file chooser dialog
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        args = {}
        if get_platform() == 'Tails':
            args['directory'] = '/home/amnesia'

        filename = QFileDialog.getOpenFileName(caption=strings.get('choose_file'), options=QFileDialog.ReadOnly, **args)
        if not filename:
            return False

        filename = str(filename)

    # validate filename
    if not os.path.isfile(filename):
        alert(strings.get("not_a_file").format(filename), QMessageBox.Warning)
        return False

    filename = os.path.abspath(filename)
    return SharedFile(filename)

def main():
    strings = onionshare.Strings()

    # start the Qt app
    app = Application()

    # check for root in Tails
    if get_platform() == 'Tails' and not is_root():
        subprocess.call(['/usr/bin/gksudo'] + sys.argv)
        return

    # create the onionshare icon
    global window_icon
    onionshare_gui_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    window_icon = QIcon("{0}/onionshare-icon.png".format(onionshare_gui_dir))

    # try starting hidden service
    service = onionshare.HiddenService.build()
    try:
       service.start()
    except onionshare.NoTor as e:
        alert(e.args[0], QMessageBox.Warning)
        return

    # select file to share
    shared_file = select_file(strings)
    if not shared_file:
        return

    # initialize the web app
    wbapp = WebApp.build(service, shared_file, app, strings)

    # run the web app in a new thread
    webapp_port = onionshare.hidden_service.choose_open_port()
    webapp_thread = WebAppThread(wbapp, webapp_port)
    webapp_thread.start()

    # clean up when app quits
    def shutdown():
        service.shutdown()
    app.connect(app, SIGNAL("aboutToQuit()"), shutdown)

    # launch the window
    web = Window(shared_file.basename, webapp_port)
    web.show()

    # all done
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
