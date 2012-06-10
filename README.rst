Socket-throttle
===============

An experiment in patching Python's socket module to create sockets that are
limited to recieving data at a certain rate.

Designed for use with HTTPConnection and associated classes, to simulate 
reading in HTTP Responses over slow running connections.

