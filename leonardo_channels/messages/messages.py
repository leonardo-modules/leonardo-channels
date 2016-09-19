'''

Implements django-messages over django-channels

'''
import json

from channels import Group


def add_message(user, level, message, extra_tags='', fail_silently=False):
    """Attempts to add a message to the request using the 'messages' app."""
    msg = {
        'message': message,
        'level': level,
        'extra_tags': extra_tags,
    }
    Group("messages-%s" %
          user.id).send({'text': json.dumps(msg)})
