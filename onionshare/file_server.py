from flask import Flask, Markup, Response, request, make_response, send_from_directory, render_template_string
from request_queue import RequestQueue
from strings import Strings

import inspect, os

class FileServer(object):

    @classmethod
    def build(self, sharedfile, requestq):
      app = Flask(__name__)

      onionshare_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
      self.download_count = 0
      strings = Strings()

      @app.route("/{0}".format(sharedfile.slug))
      def index():
          requestq.add_request(requestq.REQUEST_LOAD, request.path)
          return render_template_string(open('{0}/index.html'.format(onionshare_dir)).read(),
                  slug=sharedfile.slug, filename=sharedfile.basename, filehash=sharedfile.filehash, filesize=sharedfile.filesize, strings=strings)

      @app.route("/{0}/download".format(sharedfile.slug))
      def download():

          # each download has a unique id
          download_id = self.download_count
          self.download_count += 1

          # tell GUI the download started
          path = request.path
          requestq.add_request(requestq.REQUEST_DOWNLOAD, path, { 'id':download_id })

          dirname = sharedfile.dirname
          basename = sharedfile.basename

          def generate():
              chunk_size = 102400 # 100kb

              fp = open(sharedfile.filename, 'rb')
              done = False
              while not done:
                  chunk = fp.read(102400)
                  if chunk == '':
                      done = True
                  else:
                      yield chunk

                      # tell GUI the progress
                      requestq.add_request(requestq.REQUEST_PROGRESS, path, { 'id':download_id, 'bytes':fp.tell() })
              fp.close()

          r = Response(generate())
          r.headers.add('Content-Length', sharedfile.filesize)
          r.headers.add('Content-Disposition', 'attachment', filename=sharedfile.basename)
          return r

      @app.errorhandler(404)
      def page_not_found(e):
          requestq.add_request(requestq.REQUEST_OTHER, request.path)
          return render_template_string(open('{0}/404.html'.format(onionshare_dir)).read())

      return app
