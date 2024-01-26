# Import libraries
from flask import Flask, request
from datetime import datetime
import json
import argparse

# Arguments
argument_parser = argparse.ArgumentParser(description="Betupe is IP fishing tool. You can set up server that logs all IP addresses from requests.")
argument_parser.add_argument("--port", "-p", type=int, help="Add custom port for server")
argument_parser.add_argument("--domain", "-d", type=str, help="Add server domain to get acces to internet")
argument_parser.add_argument("--no_debug", "-nD", action="store_true", help="Turn debugging off")
argument_parser.add_argument("--path", "-fp", type=str, help="Server response file path.")
arguments = argument_parser.parse_args()

# Flask app
server = Flask(__name__)

# Server values
file = open("setup.json")
json_data = json.load(file)
port =  arguments.port or json_data["port"] or 4400
domain = arguments.domain or json_data["domain"] or "127.0.0.1"
debug = arguments.no_debug or not json_data["no_debug"] or False
return_file = arguments.path or not json_data["return_file"] or "index.html"

# GET-request handler
@server.route("/")
def get_request():
    time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file = open("data/"+str(time), "w")
    json.dump(
        {
            "time": time,
            "type": request.method,
            "ip_addr": request.remote_addr
        },
        file
    )
    file.close()
    page = open(return_file, "r")
    return page

if __name__ == "__main__":
    server.run(port=port, host=domain, debug=debug)
