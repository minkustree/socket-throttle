'''
socket-throttle.py

A replacement/wraper for socket that limits the rate at which data is received.
'''

import socket
import sys
from time import time, sleep

class ThrottledSocket(object):
    
    def __init__(self, wrappedsock):
        # Was: self._sock = sock
        # but this would have triggered setattr, so acheive the same effect: 
        self.__dict__['_wrappedsock'] = wrappedsock
        self.__dict__['_debug'] = True
        self.__dict__['max_bps'] = 1024

        
    def __getattr__(self, attr):
        return getattr(self._wrappedsock, attr)
    
    def __setattr__(self, attr, value):
        return setattr(self._wrappedsock, attr, value)       
    
    
    def recv(self, *args):
        start = time()
        buf = self._wrappedsock.recv(*args)
        end = time()
        expected_end = start + (len(buf) * 8 / self.max_bps)
        if self._debug:
            print "Actual: received %s bytes in %s seconds: rate=%sbps" % (
                len(buf), 
                end - start,
                len(buf) * 8 / (end-start) ) 
        if expected_end > end: # only sleep if recv was quicker than expected
            # assume negligable time between end and here, and that additional
            # calls to time() may end up being more lengthly than the logic
            # to determine how long to sleep for.
            if self._debug:
                print "  Sleeping % s seconds" % (expected_end - end)
            # TODO: Protect from negative sleeps?    
            sleep(expected_end - end)
        if self._debug:
            now = time()
            print "  Effective: received %s bytes in %s seconds: rate=%sbps" % (
            len(buf), 
            now - start,
            len(buf) * 8 / (now-start) )
        return buf 

    
    def makefile(self, mode='r', bufsize=-1):
        """makefile([mode[, bufsize]]) -> file object

        Return a regular file object corresponding to the socket.  The mode
        and bufsize arguments are as for the built-in open() function.
        
        File object wraps this socket, not the underlying socket implementation.
        TODO: Better doc for this
        """
        return socket._fileobject(self, mode, bufsize)
    
def make_throttled_socket(*args, **kwargs):
    return ThrottledSocket(socket._realsocket(*args, **kwargs))
        
def patch():        
    # monkey patch socket to use this type of socket for everything
    socket.socket = make_throttled_socket
    socket.SocketType = ThrottledSocket

if __name__ == '__main__':
    import httplib
    patch()
    h = httplib.HTTPConnection("www.python.org")
    h.connect()
    h.request('GET', '/')
    response = h.getresponse()
    print response 