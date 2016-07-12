import json
import logging

from channels.handler import AsgiHandler
from leonardo.utils import render_region
from leonardo_channels import Group
from leonardo_channels.auth import (channel_session_user,
                                    channel_session_user_from_http)
from django.core.cache import caches
from copy import deepcopy

LOG = logging.getLogger(__name__)

cache = caches['default']

CACHE_KEY = 'widget.content.users'
CACHE_COUNT_KEY = CACHE_KEY + '.count'


@channel_session_user_from_http
def ws_add(message):
    """
    Save all users which is connected to the cache

    users are used to rendering widgets with permissions
    """

    user = cache.get('%s.%s' % (CACHE_KEY, message.user.id))

    if not user:

        cache.set('%s.%s' %
                  (CACHE_KEY, message.user.id),
                  deepcopy(message.user), None)

        # incerement count because standard cache does not support wildcard
        count = cache.get(CACHE_COUNT_KEY)

        if not count:
            count = 1
        else:
            count += 1

        cache.set('widget.content.users.count', count, None)

    Group("widgets.content-%s" %
          message.user.username).add(message.reply_channel)


@channel_session_user
def ws_disconnect(message):

    cache.delete('widget.content.users.%s' % message.user.id)

    count = cache.get(CACHE_COUNT_KEY)

    if count:
        count -= 1
        cache.set(CACHE_KEY, count, None)

    Group("widgets.content-%s" %
          message.user.username).discard(message.reply_channel)


def widget_update(message, **kwargs):
    """render widget or widget region and send them to the clients

    this method handles post_save signals

    if instance was created render whole region

    """

    def get_request_from_message(msg):
        """returns inicialized request
        """

        request = AsgiHandler.request_class(message)

        request.frontend_editing = True

        if not hasattr(request, '_feincms_extra_context'):
            request._feincms_extra_context = {}

        from leonardo.module.web.processors.config import ContextConfig

        # call processors
        for fn in reversed(list(widget.parent.request_processors.values())):
            fn(widget.parent, request)

        request.LEONARDO_CONFIG = ContextConfig(request)

        return request

    widget = message.content['widget']

    message.content["frontend_editing"] = True
    message.content["method"] = "GET"

    request = get_request_from_message(message)

    count = cache.get(CACHE_COUNT_KEY)

    # now we render widgets for all users
    for i in range(0, count):

        user = cache.get('%s.%s' % (CACHE_KEY, i))

        if user:

            request.user = user

            if "created" in message.content or "deleted" in message.content:
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

            Group("widgets.content-%s" %
                  user.username).send({'text': json.dumps(msg)})
