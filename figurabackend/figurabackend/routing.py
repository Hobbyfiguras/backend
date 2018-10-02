# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from FigureSite.auth import TokenAuthMiddlewareStack 
from channels.routing import ProtocolTypeRouter, URLRouter
import FigureSite.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            FigureSite.routing.websocket_urlpatterns
        )
    ),
})