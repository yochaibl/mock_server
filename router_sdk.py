import httplib

import requests


class RouterConfigException(Exception):
    pass


class Route(object):
    ANY_PATH = "*"
    ANY_METHOD = "*"

    def __init__(self, path, method, response_status_code, response_data):
        self.path = path
        self.method = method
        self.response_status_code = response_status_code
        self.response_data = response_data


class RouteCreator(object):
    STATUS_CODE_KEY = "status-code"
    STATUS_DATA_KEY = "data"

    CONFIG_URL_ROUTE = "/set_routes/"

    def __init__(self, server_url):
        self._config_url = "%s%s" % (server_url, self.CONFIG_URL_ROUTE)
        self._config_dict = {}

    def add_route(self, route):
        self._config_dict[route.path] = self._config_dict.get(route.path, {})
        self._config_dict[route.path][route.method] = {
            self.STATUS_CODE_KEY: route.response_status_code,
            self.STATUS_DATA_KEY: route.response_data
        }

    def add_routes(self, routes):
        for route in routes:
            self.add_route(route)

    def set_all(self):
        response = requests.post(self._config_url, json=self._config_dict)
        if response.status_code != httplib.NO_CONTENT:
            raise RouterConfigException
