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
import signal
import sys

# Set up a quick exit
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

in_memory_datastore = {
    "Create F5 pool with 2 members": "      f5networks.f5_modules.bigip_pool:\\\\n        name: \"{{ pool_name }}\"\\\\n        partition: Common\\\\n        lb_method: \"{{ lb_method }}\"\\\\n        slow_ramp_time: \"{{ slow_ramp_time }}\"\\\\n        monitor_type: and_list\\\\n        monitors:\\\\n          - \"{{ mon }}\"\\\\n        state: present\\\\n      delegate_to: localhost" ,
    "Create F5 VIP": "      f5networks.f5_modules.bigip_virtual_server:\\\\n        name: \\\"{{ vip_name }}\\\"\\\\n        destination: \\\"{{ vip_ip }}\\\"\\\\n        port: \\\"{{ vip_port }}\\\"\\\\n        pool: \\\"{{ pool_name }}\\\"\\\\n        snat: Automap\\\\n        description: \\\"{{ vs_description }}\\\"\\\\n        all_profiles:\\\\n          - \\\"{{ profile1 }}\\\"\\\\n          - \\\"{{ profile2 }}\\\"\\\\n        state: present\\\\n      delegate_to: localhost" ,
    "Reboot F5": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Create a Cisco ACI VLAN": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Login to DB2": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Create an OpenShift namespace": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost", 
    "Create something": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Restart an nginx server": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Clear a SAP queue": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Restart a Websphere instance": "      f5networks.f5_modules.bigip_command:\\\\n        commands: tmsh reboot\\\\n      delegate_to: localhost",
    "Create a Cisco ACI tenant": "cisco.aci.aci_tenant:\\\\n  description: Tenant configured by Ansible\\\\n  host: '{{ ansible_host }}'\\\\n  password: '{{ _password_ }}'\\\\n  state: present\\\\n  tenant: CiscoLive-Demo\\\\n  username: '{{ _username_ }}'\\\\n  validate_certs: false",
    "Create Cisco ACI link level policies": "cisco.aci.aci_rest:\\\\n  content:\\\\n    fabricHIfPol:\\\\n      attributes:\\\\n        name: '{{ item.name }}'\\\\n        speed: '{{ item.speed }}'\\\\n        status: '{{ item.status }}'\\\\n  host: '{{ ansible_host }}'\\\\n  method: post\\\\n  password: '{{ password }}'\\\\n  path: /api/node/mo/uni/infra/hintfpol-{{ item.name }}.json\\\\n  username: '{{ _username_ }}'\\\\n  validate_certs: false\\\\nloop:\\\\n- format: json\\\\n  name: Link Level Policy\\\\n  speed: 100\\\\n  status: active\\\\n- format: json\\\\n  name: HintfPolicy\\\\n  speed: 10\\\\n  status: active\\\\n- format: json\\\\n  name: CDP Policy\\\\n  speed: 20\\\\n  status: active\\\\n- format: json\\\\n  name: MAC Address (MAC Address Type)\\\\n  speed: 128\\\\n  status: active\\\\n- name: Tunnelivity Policy",
    "Scale an OpenShift deployment": "openshift_scale:\\\\n  name: my-app\\\\n  namespace: my-namespace\\\\n  replicas: 5\\\\n  state: present",
    "Roll-back an OpenShift deployment": "openshift_deploy:\\\\n  latest: '{{ rollback_version }}'\\\\n  name: my-app\\\\n  namespace: my-namespace\\\\n  state: latest",
    "Deploy an SAP transport request": "community.general.sap_transport:\\\\n  transport_files:\\\\n  - K900123.COR\\\\n  transport_path: /usr/sap/trans/transport"
}

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def _jsonresponse(self, localrequest):
        logging.info("Local request: %s", localrequest)
        data = in_memory_datastore[localrequest]
        content = '{ "predictions": "' + data + '" }'
        logging.info("JSON response: %s", content)
        #content = "{ \"predictions\": \"testing\" }"
        return content
    
    def _retrieve_prompt(self, prompt):
        y = json.loads(prompt)
        logging.info("Prompt: %s", y["prompt"])
        return y["prompt"]

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
        #time.sleep(3)          # Wait for 3 seconds to mimic the real call
        self.wfile.write(self._jsonresponse(self._retrieve_prompt(post_data.decode('utf-8'))).encode('utf-8'))

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
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
