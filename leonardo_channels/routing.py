
try:
    from django.channels.routing import route, include, Route, Include
except ImportError:
    from channels.routing import route, include, Route, Include
