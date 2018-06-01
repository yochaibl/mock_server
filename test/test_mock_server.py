import httplib
import requests

from router_sdk import RouteCreator, Route
from server import defs

SERVER_URL = "http://localhost:2727"

NOT_FOUND_RESPONSE = Route.Response(
    status_code=defs.NOT_FOUND_RESPONSE_STATUS,
    data=defs.NOT_FOUND_RESPONSE_DATA
)


A_ROOT_ROUTE = Route(
    request=Route.Request(
        path="/things/a/",
        method=defs.METHOD_GET
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "root-a",
            "value": 1
        }
    )
)

A_SUB_ROUTE = Route(
    request=Route.Request(
        path="/things/a/that",
        method=defs.METHOD_GET
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "sub-a",
            "value": 1.1
        }
    )
)

B_ROUTE = Route(
    request=Route.Request(
        path="/things/b/",
        method=defs.METHOD_GET
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "b",
            "value": 2
        }
    )
)

C_ROUTE = Route(
    request=Route.Request(
        path="/things/c/",
        method=defs.METHOD_GET
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "c",
            "value": 3
        }
    )
)

D_ROUTE = Route(
    request=Route.Request(
        path="/things/d/",
        method=defs.METHOD_GET
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "d",
            "value": 4
        }
    )
)

E_ROUTE = Route(
    request=Route.Request(
        path="/things/e/",
        method=defs.METHOD_GET
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "e",
            "value": 5
        }
    )
)

E_ROUTE_ANY_METHOD = Route(
    request=Route.Request(
        path=E_ROUTE.request.path,
        method=defs.ANY_METHOD
    ),
    response=Route.Response(
        status_code=httplib.ACCEPTED,
        data={
            "name": "e-any-method",
            "value": 2.71
        }
    )
)

ANY_ROUTE_PUT = Route(
    request=Route.Request(
        path=defs.ANY_PATH,
        method=defs.METHOD_PUT
    ),
    response=Route.Response(
        status_code=httplib.OK,
        data={
            "name": "any-route-put",
            "value": -1
        }
    )
)

ANY_ROUTE_ANY_METHOD = Route(
    request=Route.Request(
        path=defs.ANY_PATH,
        method=defs.ANY_METHOD
    ),
    response=Route.Response(
        status_code=httplib.NOT_IMPLEMENTED,
        data={"not": "implemented"}
    )
)

# The following routes will not be loaded to the server, and will only be used for testing the 'any'

E_ROUTE_PUT_METHOD = Route(
    request=Route.Request(
        path=E_ROUTE.request.path,
        method=defs.METHOD_PUT,
    ),
    response=E_ROUTE_ANY_METHOD.response
)

E_ROUTE_PATCH_METHOD = Route(
    request=Route.Request(
        path=E_ROUTE.request.path,
        method=defs.METHOD_PATCH
    ),
    response=ANY_ROUTE_ANY_METHOD.response
)

B_ROUTE_GET_METHOD = Route(
    request=Route.Request(
        path=B_ROUTE.request.path,
        method=defs.METHOD_GET
    ),
    response=ANY_ROUTE_ANY_METHOD.response
)

B_ROUTE_PUT_METHOD = Route(
    request=Route.Request(
        path=B_ROUTE.request.path,
        method=defs.METHOD_PUT,
    ),
    response=ANY_ROUTE_PUT.response
)

B_ROUTE_PATCH_METHOD = Route(
    request=Route.Request(
        path=B_ROUTE.request.path,
        method=defs.METHOD_PATCH,
    ),
    response=ANY_ROUTE_ANY_METHOD.response
)

F_ROUTE_PUT_METHOD = Route(
    request=Route.Request(
        path="/things/f/",
        method=defs.METHOD_PUT,
    ),
    response=ANY_ROUTE_PUT.response
)

F_ROUTE_PATCH_METHOD = Route(
    request=Route.Request(
        path="/things/f/",
        method=defs.METHOD_PATCH,
    ),
    response=ANY_ROUTE_ANY_METHOD.response
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
        response = requests.request(method=route.request.method,
                                    url="%s%s" % (SERVER_URL, route.request.path))

        if expect_presence:
            expected_response = route.response
        else:
            expected_response = NOT_FOUND_RESPONSE

        assert expected_response.check_match(response)

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
