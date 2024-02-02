#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import logging
import json
import yaml
import signal
import sys
from time import sleep
from pathlib import Path
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio

######################################################
# Set up a quick exit
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)



######################################################
# Globals :-
# Global output file
#outputfile = logging.getLogger('log')

# Load configuration from the config file (supplied via a configmap)
#OUTPUT_FILE="/tmp/yamlstream.txt"
#LIGHTSPEED_URL="http://localhost:8000/api/v0/ai/completions/"
#RECOVERY_URL="http://recovery-service:8080/recover"
with open("/config/config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Set up a separate logging object to create a thread-safe way of writing to the
# output file.  This is separate to the "standard" logging of the service.
#outputfile = logging.getLogger('log')
#outputfile.setLevel(logging.INFO)
#ch = logging.FileHandler(config["OUTPUT_FILE"])
#ch.setFormatter(logging.Formatter('%(message)s'))
#outputfile.addHandler(ch)

# create fastapi instance
app = FastAPI()

# Create a global that holds all of the current issues that are being fixed
problems = {}


######################################################
# 
def dump_status():
    with open(config["OUTPUT_FILE"],"w") as f:
        for key, problem in problems.items():
            f.write("\n")
            if problem["state"] == "initial":
                f.write("| Detected issue with " + problem["name"] + "\n")
#                f.write("| Calculating remediation action... <img src=\"images/spinner.gif\" width=\"14\" height=\"14\">\n")
                f.write("| Calculating remediation action... \n")
            if problem["state"] == "english":
                f.write("| Detected issue with " + problem["name"] + "\n")
                f.write("| Suggestion: " + problem["request"] + "\n")
            if problem["state"] == "lightspeed":
                f.write("| Detected issue with " + problem["name"] + "\n")
                f.write("| Suggestion: " + problem["request"] + "\n")
#                f.write("| Calculating YAML... <img src=\"images/spinner.gif\" width=\"14\" height=\"14\">\n")
                f.write("| Calculating YAML... \n")
            if problem["state"] == "lightspeedreturned":
                f.write("| Detected issue with " + problem["name"] + "\n")
                f.write("| Suggestion: " + problem["request"] + "\n")
                #f.write("| Calculating YAML... done!\n")
                yaml = problem["yaml"]
                f.write("| YAML: \n" + yaml.replace("\\n", "\n") + "\n")
#                f.write("| Applying fix... <img src=\"images/spinner.gif\" width=\"14\" height=\"14\">\n")
                f.write("| Applying fix... \n")
            if problem["state"] == "fixed":
                f.write("| Detected issue with " + problem["name"] + "\n")
                f.write("| Suggestion: " + problem["request"] + "\n")
                #f.write("| Calculating YAML... done!\n")
                yaml = problem["yaml"]
                f.write("| YAML: \n" + yaml.replace("\\n", "\n") + "\n")
                f.write("| Problem fixed\n")
        if len(problems) == 0:
            f.write("Waiting Instructions...\n")
    f.close



######################################################
# 
async def log_reader(n=5) -> list:
    """Log reader

    Args:
        n (int, optional): number of lines to read from file. Defaults to 5.

    Returns:
        list: List containing last n-lines in log file with html tags.
    """
    log_lines = []
    with open(config["OUTPUT_FILE"], "r") as file:
        for line in file.readlines()[-n:]:
            if line.__contains__("ERROR"):
                log_lines.append(f'<span class="text-red-400">{line}</span><br/>')
            elif line.__contains__("WARNING"):
                log_lines.append(f'<span class="text-orange-300">{line}</span><br/>')
            elif line.startswith(" "):   # This is for the pre-formatted YAML content.  Don't put a <br> on the end because it's already wrapped in a <pre>
                log_lines.append(f"{line}")
            else:
                #log_lines.append(f"{line}\n")
                log_lines.append(f"{line}")
        return log_lines



@app.post("/")
async def get(request: Request):

    req_info = await request.json()

    resp = await process_request(req_info)

    return {
        "status" : "SUCCESS",
        "data" : req_info
    }

@app.get("/log")
async def get(request: Request):

    #req_info = await request.json()

    #resp = await process_request(req_info)

    with open(config["OUTPUT_FILE"]) as f:
        data = f.read()

    return {"data": data }

@app.websocket("/ws/log")
async def websocket_endpoint_log(websocket: WebSocket) -> None:
    """WebSocket endpoint for client connections

    Args:
        websocket (WebSocket): WebSocket request from client.
    """
    await websocket.accept()

    try:
        while True:
            #await asyncio.sleep(1)
            logs = await log_reader(30)
            await websocket.send_text(logs)
    except Exception as e:
        print(e)
    finally:
        await websocket.close()


async def process_request(data):

    logging.info("Processing request...")

    # The data is in JSON format, so strip out the request
    #y = json.loads(data)
    req = data["request"]
    deployment = data["deployment"]

    # This is the object that we'll update throughout the request processing.
    # This object gets dumped to a file and sent via WebSocket to the front-end
    problem = { "name": deployment,
                "deployment": deployment,
                "state": "initial",
                "request": req }
    problems[deployment] = problem
    dump_status()
    await asyncio.sleep(1)

    logging.info("English request: %s", req)

    problem["state"] = "english"
    problem["request"] = req
    dump_status()
    await asyncio.sleep(2)

    problem["state"] = "lightspeed"
    dump_status()
    await asyncio.sleep(3)

    # Call Lightspeed to retrieve the AAP YAML to run
    LIGHTSPEED_URL = config["LIGHTSPEED_URL"]
    lightspeed_data = { "prompt": req}
    response = requests.post(url=LIGHTSPEED_URL, json=lightspeed_data, timeout=15)
    jsonresp = response.content.decode('utf-8')
    #jsonresp = response.content
    logging.info("Raw response from lightspeed: %s", jsonresp)

    jsoncontent = json.loads(jsonresp)
    #predictions = jsonresp["predictions"]
    predictions = jsoncontent["predictions"]
    logging.info("Lightspeed prediction: %s", predictions)

    problem["yaml"] = predictions
    problem["state"] = "lightspeedreturned"
    dump_status()
    await asyncio.sleep(3)

    # Write the request to the stream file
    #outputfile.info("** Remediation request: " + req)

    # ... and the response as well
    #outputfile.info("Remediation Action: " + predictions)

    # Finally, call the system that will recover the Deployment
    logging.info("Recovering Deployment: %s", deployment)
    RECOVERY_URL = config["RECOVERY_URL"]
    recovery_data = { "recover": deployment }
    response = requests.post(url=RECOVERY_URL, json=recovery_data, timeout=15)

    problem["state"] = "fixed"
    dump_status()

    # We need to wait for a while and then clean up the remediation action
    await asyncio.sleep(2)
    del problems[deployment]
    dump_status()

    return "ok"


# set parameters to run uvicorn
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
