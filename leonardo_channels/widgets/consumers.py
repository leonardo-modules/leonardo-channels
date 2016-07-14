import json
import logging
from copy import deepcopy

from channels.generic import BaseConsumer
from channels.handler import AsgiHandler
from django.core.cache import caches
from leonardo.utils import render_region
from leonardo_channels import Group
from leonardo_channels.auth import (channel_session_user,
                                    channel_session_user_from_http)

from django.contrib.admin.util import NestedObjects
from leonardo_channels.utils import send_message


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

    if not message.user.is_authenticated():
        # for anonymous we have only one record
        message.user.id = 0

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
          message.user.id).add(message.reply_channel)


@channel_session_user
def ws_disconnect(message):

    cache.delete('widget.content.users.%s' % message.user.id)

    count = cache.get(CACHE_COUNT_KEY)

    if count:
        count -= 1
        cache.set(CACHE_KEY, count, None)

    Group("widgets.content-%s" %
          message.user.id).discard(message.reply_channel)


class SignalConsumer(BaseConsumer):

    method_mapping = {
        "http.request": "signal_reciever",
    }

    def signal_reciever(self, message, **kwargs):
        """Collect related models to instance and for widgets
        call widget_update

        in message expect:

            singal_name: string
            instance: instance
            created: bool
        """

        sender = message.content['sender']
        instance = message.content['instance']

        # page related are different because regions can inherit from parent
        # that means it's not directly connected to this page
        if sender.__name__ == "Page":

            regions = instance.content._fetch_regions()

            for region, instances in regions.items():
                for widget in instances:
                    msg = {
                        "widget": deepcopy(widget),
                        "path": "/widgets/update"}
                    send_message("http.request", msg)

            return

        # get related models and refresh it
        collector = NestedObjects(
            using=instance._state.db)  # database name

        collector.collect([instance])

        for w_cls, models in collector.data.items():
            if hasattr(w_cls, 'parent') and hasattr(w_cls, 'fe_identifier'):
                for w in models:
                    msg = {
                        "widget": w,
                        "sender": w_cls,
                        "path": "/widgets/update"}
                    send_message("http.request", msg)


class FrontendEditConsumer(BaseConsumer):

    method_mapping = {
        "http.request": "widget_update",
    }

    def signal_reciever(self, message, **kwargs):
        """This is basicaly async reciever for all signals

        in message expect:

            singal_name: string
            instance: instance
            created: bool
        """

    def widget_update(self, message, **kwargs):
        """render widget or widget region and send them to the clients

        this method handles post_save signals

        if instance was created render whole region

        """

        widget = message.content['widget']

        message.content["frontend_editing"] = True
        message.content["method"] = "GET"

        request = self.get_request_from_message(message)

        count = cache.get(CACHE_COUNT_KEY)

        keys = ['%s.%s' % (CACHE_KEY, i) for i in range(0, count)]

        # now we render widgets for all users
        for key, user in cache.get_many(keys).items():

            if user:

                request.user = user

                if "created" in message.content or "deleted" in message.content:
                    # this widget was created
                    # its simplier to render whole region instead update
                    msg = {
                        'region': '%s-%s' % (widget.region, widget.parent.slug),
                        'content': render_region(widget, request),
                    }

                else:

                    msg = {
                        'id': widget.fe_identifier,
                        'content': widget.render_content({'request': request}),
                    }

                Group("widgets.content-%s" %
                      user.id).send({'text': json.dumps(msg)})

    def get_request_from_message(self, message):
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

        request.LEONARDO_CONFIG = ContextConfig(request)

        return request
