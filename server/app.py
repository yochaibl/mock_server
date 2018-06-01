import httplib
import json
import os
from collections import namedtuple

import flask
from flask import Flask, Response

from server import defs

app = Flask(__name__)


SERVER_PORT = 2727

CONFIG_FILE_PATH = "/tmp/config.json"

RESPONSE_DATA_KEY = "data"
RESPONSE_STATUS_CODE_KEY = "status-code"


class ConfigurationError(Exception):
    pass


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


def _get_combination_config(path, method):
    return _get_config().get(path, {})[method]


CombinationAttempt = namedtuple("CombinationAttempt", ["path", "method"])


def _find_match(path, method):
    combination_check_order = [
        CombinationAttempt(path=path, method=method),
        CombinationAttempt(path=path, method=defs.ANY_METHOD),
        CombinationAttempt(path=defs.ANY_PATH, method=method),
        CombinationAttempt(path=defs.ANY_PATH, method=defs.ANY_METHOD)
    ]
    for path, method in combination_check_order:
        try:
            return _get_combination_config(path, method)
        except KeyError:
            pass

    return {
        RESPONSE_DATA_KEY: defs.NOT_FOUND_RESPONSE_DATA,
        RESPONSE_STATUS_CODE_KEY: defs.NOT_FOUND_RESPONSE_STATUS
    }


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def catch_all(path):
    request_path = "/%s" % path

    response = _find_match(path=request_path, method=flask.request.method)

    return Response(json.dumps(response[RESPONSE_DATA_KEY]),
                    status=response[RESPONSE_STATUS_CODE_KEY])


if __name__ == "__main__":
    app.run(port=SERVER_PORT, host="0.0.0.0")
