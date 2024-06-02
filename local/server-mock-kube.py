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
import subprocess
import psutil
from urllib.parse import urlparse
import urllib
from sys import argv
import yaml



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
    print('Syntax: server-mock-kube.py <port> <configfile>')
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
        # THIS IS A NO-OP NOW
        #os.system(f"/tmp/oc process -f /pod-template.yaml -p WORKLOAD_NAME={deployment} | /tmp/oc create -f - -n target")

        return "ok"

    def do_fetch_pods(self):

        # Call Kubernetes to fetch the list of pods
        retlist = []
        processes = psutil.process_iter()
        for process in processes:
            if "./workload.py" in process.cmdline():
                print(f"Process ID: {process.pid}, Name: {process.name()}, Cmd: {process.cmdline()}")
                retlist.append(process.cmdline()[2])

        print(f"Return list: {retlist}")
        retstring = '{"items":["' + "\",\"".join(retlist) + '"]}'
        print(retstring)
        return retstring

    def do_delete_pod(self, to_delete):
        logging.info("Local request: %s", to_delete)

        # Call Kubernetes to delete a pod
        retlist = []
        processes = psutil.process_iter()
        for process in processes:
            if "./workload.py" in process.cmdline():
                print(f"Process ID: {process.pid}, Name: {process.name()}, Cmd: {process.cmdline()}")
                processname = process.cmdline()[2]
                if processname == to_delete:
                    print(f"Found the process to delete: {process.pid}")
                    process.kill()
                    MOCKEDA = config["BASEDIR"] + '/mock-eda-listener.sh'
                    #pid = subprocess.Popen(['/home/damo/Project1989/project1989/alllocal/mock-eda/mock-eda-listener.sh', to_delete]).pid
                    pid = subprocess.Popen([MOCKEDA, to_delete]).pid

        return "ok"

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

        query = urlparse(self.path)
        action = urllib.parse.parse_qs(query.query)['action'][0]

        print(query)
        print(action)

        #if self.path == '/kube/pods':
        if query.path == '/kube/pods':
            if action == "list":
                getdata = self.do_fetch_pods()

            if action == "delete":
                pod_name = urllib.parse.parse_qs(query.query)['pod_name'][0]
                print(pod_name)
                getdata = self.do_delete_pod(pod_name)

        self._set_response()
        self.wfile.write(getdata.encode('utf-8'))

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
