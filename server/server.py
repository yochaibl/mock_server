import httplib
import json
import os

import flask
from flask import Flask, Response

app = Flask(__name__)


SERVER_PORT = 2727

CONFIG_FILE_PATH = "/tmp/config.json"

RESPONSE_DATA_KEY = "data"
RESPONSE_STATUS_CODE_KEY = "status-code"
NOT_FOUND_RESPONSE = {"error": "not found"}


def _get_config():
    if not os.path.exists(CONFIG_FILE_PATH):
        return {}

    with open(CONFIG_FILE_PATH, "rb") as config_file:
        return json.load(config_file)


@app.route("/set_routes/", methods=["POST"])
def set_routes():
    with open(CONFIG_FILE_PATH, "wb") as config_file:
        json.dump(flask.request.json, config_file)

    return Response(status=httplib.NO_CONTENT)


@app.route("/get_routes", methods=["get"])
def get_routes():
    return Response(_get_config())


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    request_path = "/%s" % path
    registered_response = _get_config().get(request_path, {}).get(flask.request.method)

    if not registered_response:
        return Response(json.dumps(NOT_FOUND_RESPONSE), status=httplib.NOT_FOUND)

    return Response(json.dumps(registered_response[RESPONSE_DATA_KEY]),
                    status=registered_response[RESPONSE_STATUS_CODE_KEY])


if __name__ == "__main__":
    app.run(port=SERVER_PORT, host="0.0.0.0")
