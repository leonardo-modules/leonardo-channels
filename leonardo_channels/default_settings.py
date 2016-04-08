

try:
    import asgi_redis
    BACKEND = "asgi_redis.RedisChannelLayer"
    CONFIG = {
        "hosts": [("localhost", 6379)],
    }
except ImportError:
    BACKEND = "asgiref.inmemory.ChannelLayer"
    CONFIG = {}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": BACKEND,
        "CONFIG": CONFIG,
        "ROUTING": "leonardo_channels.routes.channel_routing",
    },
}
