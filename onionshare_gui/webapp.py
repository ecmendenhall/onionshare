from flask import Flask, render_template
import threading, json, os, time, platform, sys
import onionshare.request_queue
from onionshare.request_queue import RequestQueue
from onionshare.strings import Strings
from onionshare.file_server import FileServer

def get_temp_dir():
    # figure out this platform's temp dir
    if platform.system() == 'Windows':
        return os.environ['Temp'].replace('\\', '/')
    else:
        return '/tmp/'

temp_dir = get_temp_dir()

def suppress_output():
    # suppress output in windows
    if platform.system() == 'Windows':
        sys.stdout = open('{0}/onionshare.stdout.log'.format(temp_dir), 'w')
        sys.stderr = open('{0}/onionshare.stderr.log'.format(temp_dir), 'w')

suppress_output()

# log web errors to file
import logging
log_handler = logging.FileHandler('{0}/onionshare.web.log'.format(temp_dir))
log_handler.setLevel(logging.WARNING)

class WebApp:

    @classmethod
    def build(self, hidden_service, shared_file, qtapp):
        strings = Strings()
        clipboard = qtapp.clipboard()

        app = Flask(__name__, template_folder='./templates')
        app.logger.addHandler(log_handler)

        url = 'http://{0}/{1}'.format(hidden_service.host, shared_file.slug)
        requestq = RequestQueue()
        os_app = FileServer.build(shared_file, requestq)

        @app.route("/")
        def index():
            return render_template('index.html')

        @app.route("/init_info")
        def init_info():
            return json.dumps({
                'strings': strings.strings,
                'basename': shared_file.basename
            })

        @app.route("/start_onionshare")
        def start_onionshare():

            # start onionshare service in new thread
            print hidden_service.host + '/' + shared_file.slug
            t = threading.Thread(target=os_app.run, kwargs={'port': hidden_service.port})
            t.daemon = True
            t.start()

            return json.dumps({
                'filehash': shared_file.filehash,
                'filesize': shared_file.filesize,
                'url': url
            })

        @app.route("/copy_url")
        def copy_url():
            clipboard.setText(url)
            return ''

        @app.route("/heartbeat")
        def check_for_requests():
            events = []

            done = False
            while not done:
                try:
                    r = requestq.q.get(False)
                    events.append(r)
                except onionshare.request_queue.Queue.Empty:
                    done = True

            return json.dumps(events)

        @app.route("/close")
        def close():
            time.sleep(1)
            qtapp.closeAllWindows()
            return ''

        return app
