import json
import logging

from django.contrib.admin.util import NestedObjects
from leonardo.utils import render_region
from leonardo_channels import Group
from leonardo_channels.auth import (channel_session_user,
                                    channel_session_user_from_http)
from leonardo_channels.consumers import LeonardoPageConsumer, ModelConsumer
from leonardo_channels.managers import users

LOG = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_add(message):
    """
    Save all users which is connected to the cache

    users are used to rendering widgets with permissions
    """

    if not message.user.is_authenticated():
        # for anonymous we have only one record
        message.user.id = 0

    users.add(message.user)

    Group("widgets.content-%s" %
          message.user.id).add(message.reply_channel)


@channel_session_user
def ws_disconnect(message):

    users.delete(message.user)

    Group("widgets.content-%s" %
          message.user.id).discard(message.reply_channel)


class SignalConsumer(ModelConsumer):

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

        instance = self.get_instance(
            message.content['sender'],
            message.content['instance'])

        # page related are different because regions can inherit from parent
        # that means it's not directly connected to this page
        if instance.__class__.__name__ == "Page":

            regions = instance.content._fetch_regions()

            for region, instances in regions.items():
                for widget in instances:
                    msg = {
                        "widget": widget,
                        "sender": widget.__class__,
                        "path": "/widgets/update"}
                    self.sender.send("http.request", msg)

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
                    self.sender.send("http.request", msg)


class FrontendEditConsumer(LeonardoPageConsumer):

    method_mapping = {
        "http.request": "widget_update",
    }

    def widget_update(self, message, **kwargs):
        """render widget or widget region and send them to the clients

        this method handles post_save signals

        if instance was created render whole region

        """

        widget = self.get_instance(
            message.content['sender'],
            message.content['widget'])

        message.content["frontend_editing"] = True
        message.content["method"] = "GET"

        # now we render widgets for all users
        for user in users.all():

            request = self.get_request_from_message(message, widget, user)

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
