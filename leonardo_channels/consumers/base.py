import logging

from channels.generic import BaseConsumer
from channels.handler import AsgiHandler
from django.apps import apps
from django.core.handlers.base import BaseHandler
from django.forms import modelform_factory
from leonardo.module.web.processors.config import ContextConfig
from leonardo_channels.senders import sender

LOG = logging.getLogger(__name__)


class ModelConsumer(BaseConsumer):

    sender = sender

    def get_instance(self, cls, data):
        """return inicialized instance
        """
        cls = self.get_class(cls)
        # this not works for post_delete signal

        try:
            instance = cls.objects.get(id=data['id'])
        except cls.DoesNotExist:
            instance = cls(**self.get_model_data(cls, data))

        return instance

    def get_model_data(self, cls, data):

        FormCls = self.get_model_form_cls(cls)
        form = FormCls(data)

        if form.is_valid():
            return form.cleaned_data

        raise Exception(form.errors)

    def get_model_form_cls(self, cls):
        return modelform_factory(cls, exclude=tuple())

    def get_class(self, cls_name):
        app_label, model_name = cls_name.split('.')
        return apps.get_model(app_label, model_name)


class LeonardoPageConsumer(ModelConsumer):

    def get_request_from_message(self, message, widget, user):
        """returns inicialized request
        """

        request = AsgiHandler.request_class(message)

        request.user = user
        request.path = widget.parent.get_absolute_url()
        request.frontend_editing = True

        if not hasattr(request, '_feincms_extra_context'):
            request._feincms_extra_context = {}

        # call processors
        for fn in reversed(list(widget.parent.request_processors.values())):
            fn(widget.parent, request)

        request.LEONARDO_CONFIG = ContextConfig(request)

        # this breaks all get_absolute_uri calls
        request.META['SERVER_NAME'] = 'localhost'
        request.META['SERVER_PORT'] = 80

        handler = BaseHandler()
        handler.load_middleware()

        # Apply request middleware
        for middleware_method in handler._request_middleware:
            try:
                middleware_method(request)
            except:
                pass

        # we know that we are in editing mode and user is logged in
        request.frontend_editing = True
        request.user = user

        # call processors
        for fn in reversed(list(widget.parent.request_processors.values())):
            fn(widget.parent, request)

        if hasattr(widget, 'process') and callable(widget.process):
            widget.process(request, view=self)

        return request
