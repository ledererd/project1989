#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import time
import os
import signal
import sys
import yaml
from sys import argv

######################################################
# Set up a quick exit
def signal_handler(sig, frame):
    print('Terminating')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if len(argv) == 3:
    PORT=int(argv[1])
    CONFIG=argv[2]
else:
    print('Syntax: server-recovery-engine.py <port> <configfile>')
    sys.exit(0)


with open(CONFIG, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


######################################################

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def _response(self, localrequest):
        logging.info("Local request: %s", localrequest)
        y = json.loads(localrequest)
        deployment = y["recover"]

        # Call Kubernetes to create a Deployment
        print(f"Creating new process for: {deployment}")
        BASEDIR = config["BASEDIR"]
        os.system(f"{BASEDIR}/run-workload.sh {deployment}")
        print("Back")

        return "ok"

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()

        self.wfile.write(self._response(post_data.decode('utf-8')).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':

    run(port=PORT)
