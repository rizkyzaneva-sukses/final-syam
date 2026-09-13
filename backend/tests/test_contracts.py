"""Integration contracts independent of individual mutation implementations."""
import re
from fastapi.routing import APIRoute


def test_every_business_endpoint_requires_authentication(client):
    from app.main import app
    from fastapi.routing import _IncludedRouter

    def iter_routes(routes, prefix=""):
        for route in routes:
            if isinstance(route, _IncludedRouter):
                yield from iter_routes(
                    route.original_router.routes,
                    prefix + route.include_context.prefix,
                )
            else:
                yield prefix + (route.path or ""), route

    checked = 0
    for route_path, route in iter_routes(app.routes):
        if not isinstance(route, APIRoute) or not route_path.startswith("/api/"):
            continue
        if route_path in {"/api/health", "/api/auth/login"}:
            continue
        path = re.sub(r"\{[^}]+\}", "1", route_path)
        for method in route.methods:
            response = client.request(method, path, json={} if method in {"POST", "PATCH", "PUT"} else None)
            assert response.status_code == 401, (method, path, response.status_code, response.text)
            checked += 1
    assert checked > 50


def test_api_security_headers_and_unknown_routes(client):
    response = client.get("/api/orders")
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert client.get("/api/nonexistent-module").status_code == 404
