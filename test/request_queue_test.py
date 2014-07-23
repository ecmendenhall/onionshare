from onionshare.request_queue import *

def test_queue_enqueues_requests():
    queue = RequestQueue()
    queue.add_request('type', 'path', 'data')
    assert queue.q.get() == {'path': 'path', 'type': 'type', 'data': 'data'}
