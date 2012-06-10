'''
socket-throttle.py

A replacement/wraper for socket that limits the rate at which data is received.
'''

import socket
import sys
from time import time, sleep

class ThrottledSocket(socket.socket):
    _debug = True;
    max_bps = 1024
    
    def recv(self, *args):
        start = time()
        buf = super(socket_throttle, self).recv(*args)
        end = time()
        expected_end = start + (len(buf) * 8 * self.max_bps)
        if _debug:
            print "Actual: received %s bytes in %s seconds: rate=%sbps" % (
                len(buf), 
                end - start,
                len(buf) * 8 / (end-start) ) 
        if expected_end > end: # only sleep if recv was quicker than expected
            # assume negligable time between end and here, and that additional
            # calls to time() may end up being more lengthly than the logic
            # to determine how long to sleep for.
            if _debug:
                print "  Sleeping % s seconds" % (len(buf), end - start)
            sleep(end - expected_end)
        if _debug:
            now = time()
            print "  Effective: received %s bytes in %s seconds: rate=%sbps" % (
            len(buf), 
            now - start,
            len(buf) * 8 / (now-start) ) 

        
    def dup(self):
        """
        dup() -> throttled socket object

        Return a new throtttled socket object connected to the same system 
        resource.
        """
        return ThrottledSocket(_sock=self._sock)
    
    def makefile(self, mode='r', bufsize=-1):
        """makefile([mode[, bufsize]]) -> file object

        Return a regular file object corresponding to the socket.  The mode
        and bufsize arguments are as for the built-in open() function.
        
        File object wraps this socket, not the underlying socket implementation.
        TODO: Better doc for this
        """
        return socket._fileobject(self, mode, bufsize)
        
def patch():        
    # monkey patch socket to use this type of socket for everything
    socket.socket = ThrottledSocket
    socket.SocketType = ThrottledSocket

if __name__ == '__main__':
    import httplib
    patch()
    h = httplib.HTTPConnection("www.python.org")
    h.connect()
    h.request('GET', '/')
    response = h.getresponse()
    print response 