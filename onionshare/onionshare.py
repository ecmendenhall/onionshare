import sys

from argument_parser import ArgumentParser
from file_server import FileServer
from hidden_service import HiddenService
from request_queue import RequestQueue
from shared_file import SharedFile
from strings import Strings

class NoTor:
    pass

def load_file(filename):
    try:
        return SharedFile(filename)
    except NoFile as e:
        sys.exit(strings.get("not_a_file").format(filename))

def print_startup_message(strings, service, shared_file):
    print '\n' + strings.get("give_this_url")
    print 'http://{0}/{1}'.format(service.host, shared_file.slug)
    print ''
    print strings.get("ctrlc_to_stop")

def main():
    filename, local_only = ArgumentParser().parse()

    strings = Strings()
    service = HiddenService.build(local_only)
    shared_file = load_file(filename)

    print strings.get("calculating_sha1")

    service.start()
    print_startup_message(strings, service, shared_file)

    requestq = RequestQueue()
    server = FileServer.build(shared_file, requestq)
    server.run(port=service.port)
    print '\n'

    service.shutdown()

if __name__ == '__main__':
    main()
