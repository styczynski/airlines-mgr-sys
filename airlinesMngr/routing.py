from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import airlines


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
          airlines.routing.websocket_urlpatterns
        )
    ),
    "channel": ChannelNameRouter({
        "server_status_listeners": airlines.routing.main_channel_consumer
    })
})