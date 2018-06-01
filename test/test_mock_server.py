import httplib
import requests

from router_sdk import RouteCreator, Route
from server import defs

SERVER_URL = "http://localhost:2727"


A_ROOT_ROUTE = Route(
    path="/things/a/",
    method=defs.METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "root-a",
        "value": 1
    }
)

A_SUB_ROUTE = Route(
    path="/things/a/that",
    method=defs.METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "sub-a",
        "value": 1.1
    }
)

B_ROUTE = Route(
    path="/things/b/",
    method=defs.METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "b",
        "value": 2
    }
)

C_ROUTE = Route(
    path="/things/c/",
    method=defs.METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "c",
        "value": 3
    }
)

D_ROUTE = Route(
    path="/things/d/",
    method=defs.METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "d",
        "value": 4
    }
)

E_ROUTE = Route(
    path="/things/e/",
    method=defs.METHOD_GET,
    response_status_code=httplib.OK,
    response_data={
        "name": "e",
        "value": 5
    }
)

E_ROUTE_ANY_METHOD = Route(
    path=E_ROUTE.path,
    method=defs.ANY_METHOD,
    response_status_code=httplib.ACCEPTED,
    response_data={
        "name": "e-any-method",
        "value": 2.71
    }
)

ANY_ROUTE_PUT = Route(
    path=defs.ANY_PATH,
    method=defs.METHOD_PUT,
    response_status_code=httplib.OK,
    response_data={
        "name": "any-route-put",
        "value": -1
    }
)

ANY_ROUTE_ANY_METHOD = Route(
    path=defs.ANY_PATH,
    method=defs.ANY_METHOD,
    response_status_code=httplib.NOT_IMPLEMENTED,
    response_data={"not": "implemented"}
)

# The following routes will not be loaded to the server, and will only be used for testing the 'any'

E_ROUTE_PUT_METHOD = Route(
    path=E_ROUTE.path,
    method=defs.METHOD_PUT,
    response_status_code=E_ROUTE_ANY_METHOD.response_status_code,
    response_data=E_ROUTE_ANY_METHOD.response_data
)

E_ROUTE_PATCH_METHOD = Route(
    path=E_ROUTE.path,
    method=defs.METHOD_PATCH,
    response_status_code=ANY_ROUTE_ANY_METHOD.response_status_code,
    response_data=ANY_ROUTE_ANY_METHOD.response_data
)

B_ROUTE_GET_METHOD = Route(
    path=B_ROUTE.path,
    method=defs.METHOD_GET,
    response_status_code=ANY_ROUTE_ANY_METHOD.response_status_code,
    response_data=ANY_ROUTE_ANY_METHOD.response_data
)

B_ROUTE_PUT_METHOD = Route(
    path=B_ROUTE.path,
    method=defs.METHOD_PUT,
    response_status_code=ANY_ROUTE_PUT.response_status_code,
    response_data=ANY_ROUTE_PUT.response_data
)

B_ROUTE_PATCH_METHOD = Route(
    path=B_ROUTE.path,
    method=defs.METHOD_PATCH,
    response_status_code=ANY_ROUTE_ANY_METHOD.response_status_code,
    response_data=ANY_ROUTE_ANY_METHOD.response_data
)

F_ROUTE_PUT_METHOD = Route(
    path="/things/f/",
    method=defs.METHOD_PUT,
    response_status_code=ANY_ROUTE_PUT.response_status_code,
    response_data=ANY_ROUTE_PUT.response_data
)

F_ROUTE_PATCH_METHOD = Route(
    path="/things/f/",
    method=defs.METHOD_PATCH,
    response_status_code=ANY_ROUTE_ANY_METHOD.response_status_code,
    response_data=ANY_ROUTE_ANY_METHOD.response_data
)


DEFAULT_ROUTES = [E_ROUTE_ANY_METHOD, ANY_ROUTE_PUT, ANY_ROUTE_ANY_METHOD]


ABC_ROUTES = [A_ROOT_ROUTE, A_SUB_ROUTE, B_ROUTE, C_ROUTE]
CDE_ROUTES = [C_ROUTE, D_ROUTE, E_ROUTE]
ABC_ONLY_ROUTES = set(ABC_ROUTES) - set(CDE_ROUTES)
CDE_ONLY_ROUTES = set(CDE_ROUTES) - set(ABC_ROUTES)
ANY_UNLOADED_ROUTES = [
    E_ROUTE_PUT_METHOD,
    B_ROUTE_GET_METHOD,
    B_ROUTE_PUT_METHOD,
    B_ROUTE_PATCH_METHOD,
    F_ROUTE_PUT_METHOD,
    F_ROUTE_PATCH_METHOD
]


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
            expected_response_data = defs.NOT_FOUND_RESPONSE

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

    def _test_cde_with_any(self):
        self._set_routes(CDE_ROUTES + DEFAULT_ROUTES)
        self._validate_routes(CDE_ROUTES, expect_presence=True)
        self._validate_routes(ANY_UNLOADED_ROUTES, expect_presence=True)

    def test_mock_server(self):
        self._test_abc()
        self._test_cde()
        self._test_abc()
        self._test_cde_with_any()
