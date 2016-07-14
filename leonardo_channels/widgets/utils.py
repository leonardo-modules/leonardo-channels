from channels.handler import AsgiHandler


def get_request_from_message(message):
    """returns inicialized request
    """

    request = AsgiHandler.request_class(message)

    widget = message.content['widget']

    request.frontend_editing = True

    if not hasattr(request, '_feincms_extra_context'):
        request._feincms_extra_context = {}

    from leonardo.module.web.processors.config import ContextConfig

    # call processors
    for fn in reversed(list(widget.parent.request_processors.values())):
        fn(widget.parent, request)

    from django.core.handler.base import BaseHandler
    handler = BaseHandler()
    handler.load_middleware()

    # Apply request middleware
    for middleware_method in handler._request_middleware:
        middleware_method(request)

    request.LEONARDO_CONFIG = ContextConfig(request)

    return request
