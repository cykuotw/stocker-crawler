import http.server
import requests
import os
import threading
import json
from socketserver import ThreadingMixIn
from urllib.parse import unquote, parse_qs
from crawler import crawlCriticalInformation

class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."

class CriticalInfoServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api':
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            self.wfile.write(json.dumps({'安安': '你好'}).encode(encoding='utf_8'))
            return
        else:    
            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()

            df = crawlCriticalInformation()
            json_str = df.to_json()
            #print(df)
            #self.wfile.write(json_str.encode(encoding='utf_8'))
            self.wfile.write(json_str.encode(encoding='Big5'))
        


if __name__ == '__main__':
    server_address = ('', int(os.environ.get('PORT', '8000')))
    #httpd = http.server.HTTPServer(server_address, Shortener)
    httpd = ThreadHTTPServer(server_address, CriticalInfoServer)
    httpd.serve_forever()