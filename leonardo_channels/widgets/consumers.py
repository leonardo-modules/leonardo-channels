import json
import logging

from channels.handler import AsgiHandler
from leonardo.utils import render_region
from leonardo_channels import Group
from leonardo_channels.auth import (channel_session_user,
                                    channel_session_user_from_http)

LOG = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_add(message):
    # Add them to the right group
    Group("widgets.content").add(message.reply_channel)


@channel_session_user
def ws_disconnect(message):
    Group("widgets.content").discard(message.reply_channel)


def widget_update(message, **kwargs):
    """render widget or widget region and send them to the clients

    this method handles post_save signals

    if instance was created render whole region

    """

    print message.content

    widget = message.content['widget']

    message.content["frontend_editing"] = True

    message.content["method"] = "GET"

    request = AsgiHandler.request_class(message)

    request.frontend_editing = True

    if not hasattr(request, '_feincms_extra_context'):
        request._feincms_extra_context = {}

    from leonardo.module.web.processors.config import ContextConfig

    # call processors
    for fn in reversed(list(widget.parent.request_processors.values())):
        fn(widget.parent, request)

    request.LEONARDO_CONFIG = ContextConfig(request)

    if "created" in message.content:
        # this widget was created
        # its simplier to render whole region instead update
        msg = {
            'region': widget.region,
            'content': render_region(widget, request),
        }

    else:

        msg = {
            'id': widget.fe_identifier,
            'content': widget.render_content({'request': request}),
        }

    Group("widgets.content").send({'text': json.dumps(msg)})
