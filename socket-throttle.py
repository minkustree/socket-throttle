'''
socket-throttle.py

A replacement/wraper for socket that limits the rate at which data is received.
'''

import socket
from time import time, sleep

class ThrottledSocket(socket.socket):
    max_bps = 1024
    
    def recv(self, *args):
        start = time()
        buf = super(socket_throttle, self).recv(*args)
        end = time()
        expected_end = start + (len(buf) * 8 * self.max_bps)
        if expected_end > end: # only sleep if recv was quicker than expected
            # assume negligable time between end and here, and that additional
            # calls to time() may end up being more lengthly than the logic
            # to determine how long to sleep for.
            sleep(end - expected_end)
        
    def dup(self):
        """
        dup() -> throttled socket object

        Return a new throtttled socket object connected to the same system 
        resource.
        """
        return ThrottledSocket(_sock=self._sock)
        
# monkey patch socket to use this type of socket for everything
socket.socket = socket.SocketType = ThrottledSocket
 