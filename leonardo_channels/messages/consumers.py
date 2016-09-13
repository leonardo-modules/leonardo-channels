from channels import Group


import logging
from channels.auth import channel_session_user, channel_session_user_from_http

LOG = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_add(message):
    # Add them to the right group
    Group("messages-%s" % message.user.id).add(message.reply_channel)


@channel_session_user
def ws_disconnect(message):
    Group("messages-%s" %
          message.user.id).discard(message.reply_channel)
