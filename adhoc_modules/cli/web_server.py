# -*- encoding: utf-8 -*-
import sys
import BaseHTTPServer
# import SimpleHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


# class MyHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         # redirect anything any url different from main to main
#         if self.path != '/':
#             self.send_response(302)
#             self.send_header("Location", '/')
#             self.end_headers()
#             return
#         # render index on main
#         self.send_response(200)
#         self.send_header('Content-type', 'text/html')
#         self.end_headers()
#         from os import curdir, sep
#         f = open(curdir + sep + 'index.html')
#         self.wfile.write(f.read())
#         f.close()
#         return

# no lo usamos al final, tenemos que mejorarlo porque no renderiza imagen
# if we use SimpleHTTPRequestHandler it will work but only for main page


# HandlerClass = MyHTTPRequestHandler
HandlerClass = SimpleHTTPRequestHandler
ServerClass = BaseHTTPServer.HTTPServer
Protocol = "HTTP/1.0"

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8069
server_address = ('0.0.0.0', port)

HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, HandlerClass)

sa = httpd.socket.getsockname()
# print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()
