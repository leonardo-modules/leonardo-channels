
try:
    from django.channels.auth import *
except ImportError:
    from channels.auth import *
