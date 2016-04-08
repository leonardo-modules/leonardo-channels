

from leonardo_channels.router import router

# We must prevent circural imports with main routing module
channel_routing = router.routes
