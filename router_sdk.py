import httplib

import requests


class RouterConfigException(Exception):
    pass


class Route(object):
    class Request(object):
        def __init__(self, path, method):
            self.path = path
            self.method = method

    class Response(object):
        def __init__(self, data, status_code):
            self.data = data
            self.status_code = status_code

        def check_match(self, requests_response):
            return requests_response.status_code == self.status_code \
                and requests_response.json() == self.data

    def __init__(self, request, response):
        self.request = request
        self.response = response


class RouteCreator(object):
    STATUS_CODE_KEY = "status-code"
    STATUS_DATA_KEY = "data"

    CONFIG_URL_ROUTE = "/set_routes/"

    def __init__(self, server_url):
        self._config_url = "%s%s" % (server_url, self.CONFIG_URL_ROUTE)
        self._config_dict = {}

    def add_route(self, route):
        self._config_dict[route.request.path] = self._config_dict.get(route.request.path, {})
        self._config_dict[route.request.path][route.request.method] = {
            self.STATUS_CODE_KEY: route.response.status_code,
            self.STATUS_DATA_KEY: route.response.data
        }

    def add_routes(self, routes):
        for route in routes:
            self.add_route(route)

    def set_all(self):
        response = requests.post(self._config_url, json=self._config_dict)
        if response.status_code != httplib.NO_CONTENT:
            raise RouterConfigException
