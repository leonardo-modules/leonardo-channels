import json
import inspect
from django.db import models
from django.core import serializers
from leonardo_channels import Channel


class ModelSender(object):

    """Channel sender with model serialization
    """

    def process_message(self, message):
        """serialize message

        handle django model classes and instances
        """

        msg = {}

        for key, value in message.items():

            if inspect.isclass(value):

                msg[key] = self.get_model_name(value)

            elif isinstance(value, models.Model):

                msg[key] = json.loads(serializers.serialize(
                    'json', [value, ]))[0]['fields']
                msg[key]['id'] = value.pk

            elif isinstance(value, (frozenset, set, tuple,)):

                msg[key] = list(value)

            else:
                msg[key] = value

        return msg

    def send(self, path, message):
        """wrapper around standard channel send
        """

        msg = self.process_message(message)

        try:
            Channel(path).send(msg)
        except Exception as e:
            # TODO handle channel error more properly
            raise e

    def get_model_name(self, instance):
        return '.'.join([
            instance._meta.app_label,
            instance._meta.model_name])

sender = ModelSender()
