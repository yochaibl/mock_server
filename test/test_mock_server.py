import httplib
import requests

from router_sdk import RouteCreator, Route
from server.server import NOT_FOUND_RESPONSE

SERVER_URL = "http://localhost:2727"

METHOD_GET = "GET"
METHOD_POST = "POST"


A_ROOT_ROUTE = Route(
    path="/things/a/",
    method=METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "root-a",
        "value": 1
    }
)
A_SUB_ROUTE = Route(
    path="/things/a/that",
    method=METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "sub-a",
        "value": 1.1
    }
)
B_ROUTE = Route(
    path="/things/b/",
    method=METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "b",
        "value": 2
    }
)
C_ROUTE = Route(
    path="/things/c/",
    method=METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "c",
        "value": 3
    }
)
D_ROUTE = Route(
    path="/things/d/",
    method=METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "d",
        "value": 4
    }
)
E_ROUTE = Route(
    path="/things/e/",
    method=METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "e",
        "value": 5
    }
)

ABC_ROUTES = [A_ROOT_ROUTE, A_SUB_ROUTE, B_ROUTE, C_ROUTE]
CDE_ROUTES = [C_ROUTE, D_ROUTE, E_ROUTE]
ABC_ONLY_ROUTES = set(ABC_ROUTES) - set(CDE_ROUTES)
CDE_ONLY_ROUTES = set(CDE_ROUTES) - set(ABC_ROUTES)


class TestMockServer(object):
    @staticmethod
    def _set_routes(routes):
        route_creator = RouteCreator(server_url=SERVER_URL)
        route_creator.add_routes(routes)
        route_creator.set_all()

    @classmethod
    def _validate_routes(cls, routes, expect_presence):
        for route in routes:
            cls._validate_route(route, expect_presence)

    @staticmethod
    def _validate_route(route, expect_presence):
        response = requests.request(method=route.method,
                                    url="%s%s" % (SERVER_URL, route.path))

        if expect_presence:
            expected_status_code = route.response_status_code
            expected_response_data = route.response_data
        else:
            expected_status_code = httplib.NOT_FOUND
            expected_response_data = NOT_FOUND_RESPONSE

        assert response.status_code == expected_status_code
        assert response.json() == expected_response_data

    def _test_abc(self):
        self._set_routes(ABC_ROUTES)
        self._validate_routes(ABC_ROUTES, expect_presence=True)
        self._validate_routes(CDE_ONLY_ROUTES, expect_presence=False)

    def _test_cde(self):
        self._set_routes(CDE_ROUTES)
        self._validate_routes(CDE_ROUTES, expect_presence=True)
        self._validate_routes(ABC_ONLY_ROUTES, expect_presence=False)

    def test_mock_server(self):
        self._test_abc()
        self._test_cde()
        self._test_abc()
