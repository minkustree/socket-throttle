'''
socket-throttle.py

A replacement/wraper for socket that limits the rate at which data is received.
'''

import socket
import sys
from time import time, sleep

class ThrottledSocket(object):
    
    def __init__(self, wrappedsock, rx_bps_max = 10 * 1024):
        '''
        rx_bps_max: Maximum number of bits per second to receive, above which 
                    we attempt to throttle. Algorithm is such that rate can not
                    be precisely guaranteed. Defaults to 10240 ( = 10 Kbps) 
        '''
        # Was: self._sock = sock
        # but this would have triggered setattr, so acheive the same effect: 
        self.__dict__['_wrappedsock'] = wrappedsock
        self.__dict__['_debug'] = False
        # We convert to bytes to make maths a little quicker in the middle
        # of the recv call. Div by 8.0 not 8 to ensure a float. If integer, 
        # all our expected durations get rounded to integer values.
        self.__dict__['max_bytes_per_sec'] = rx_bps_max / 8.0

    def __getattr__(self, attr):
        return getattr(self._wrappedsock, attr)
    
    def __setattr__(self, attr, value):
        return setattr(self._wrappedsock, attr, value)       
    
    
    def recv(self, *args):
        start = time()
        buf = self._wrappedsock.recv(*args)
        end = time()
        expected_end = start + (len(buf) / self.max_bytes_per_sec)
        if self._debug:
            duration = end - start
            if duration == 0:
                rate = "infinite"
            else:
                rate = len(buf) / duration / 1024
            print "Start: %s, End: %s, Expected end: %s" % (start, end,
                expected_end)
            print "Actual: received %s bytes in %s seconds: rate=%sKB/s" % (
                len(buf), duration, rate ) 
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
            duration = now - start
            if duration == 0:
                rate = "infinite"
            else:
                rate = len(buf) / duration / 1024
            print "Effective: received %s bytes in %s seconds: rate=%sKB/s" % (
                len(buf), duration, rate )
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
    ''' 
    Create a wrapped _realsocket that throttles received data rate to 5KB/s
    '''
    return ThrottledSocket(socket._realsocket(*args, **kwargs), 5 * 8 * 1024)
        
def patch():
    '''
    Monkey patch socket to ensure that all new sockets created are throttled
    sockets.
    '''
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
    start = time()
    data = response.read()
    end = time()
    print "Response %s bytes in %s sec (%sKB/s)" % (len(data), end-start, 
        len(data) / (end-start) /1024)
    