# Import libraries
from flask import Flask, request
from wsgiref.simple_server import make_server
from datetime import datetime
import json
import argparse

# Arguments
argument_parser = argparse.ArgumentParser(description="Betupe is IP fishing tool. You can set up server that logs all IP addresses from requests.")
argument_parser.add_argument("--port", "-p", type=int, help="Add custom port for server")
argument_parser.add_argument("--domain", "-d", type=str, help="Add server domain to get acces to internet")
argument_parser.add_argument("--no_debug", "-nD", action="store_true", help="Turn debugging off")
argument_parser.add_argument("--path", "-fp", type=str, help="Server response file path.")
argument_parser.add_argument("--local", "-l", action="store_true", help="Use test server to develop")
argument_parser.add_argument("--page-type", "-pT", type=str, help="Change type of your page on WSGI, default: text/html")
arguments = argument_parser.parse_args()

# Server values
file = open("setup.json")
json_data = json.load(file)
port =  arguments.port or json_data["port"] or 4400
domain = arguments.domain or json_data["domain"] or "127.0.0.1"
debug = arguments.no_debug or not json_data["no_debug"] or False
return_file = arguments.path or not json_data["return_file"] or "index.html"
public = not arguments.local or json_data["public"] or True
page_type = arguments.page_type or json_data["page_type"] or "text/html"


# Flask local server
if not public:
    # Flask app
    server = Flask(__name__)

    # Request handler
    @server.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE", "CONNECT"])
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
        if request.method == "GET":
            page = open(return_file, "r")
            return page
        else:
            return "non supported reguest type"
    
    # Start Flask server
    server.run(port=port, host=domain, debug=debug)

# WSGI public server
else:
    # Request handler
    def response_app(environ, response_start):
        status = "200 ok"
        headers = [("Content-type", page_type)]
        method = environ.get("REQUEST_METHOD", "GET")
        response_start(status, headers)
        time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file = open("data/"+str(time), "w")
        remote_addr = environ.get("REMOTE_ADDR", "Unknown")
        json.dump(
            {
                "time": time,
                "type": method,
                "ip_addr": remote_addr
            },
            file
        )
        file.close()
        if method == "GET":
            with open(return_file, "r") as page:
                page_inner = page.read().encode("utf-8")
                return [page_inner]
        return [b"non supported request type"]

    # WSGI app
    server = make_server(host=domain, port=port, app=response_app)
    server.serve_forever()
    print("Press CTRL+C to close program")