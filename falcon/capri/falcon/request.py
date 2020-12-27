import falcon
from typing import Any, Callable
from capri.core import Context


def create_http_request_factory(context_factory: Callable, context_iface: Any):
    def http_request_factory(app):
        class HttpRequest(falcon.Request):
            def context_factory(request) -> Context:
                return app.create_context(
                    context_factory,
                    context_iface,
                    request)
            context_type = context_factory
        return HttpRequest
    return http_request_factory
