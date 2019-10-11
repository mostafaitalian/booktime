from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from . import auth
import main.routing

application = ProtocolTypeRouter({
    "websocket": auth.TokenGetAuthMiddleware(
        URLRouter(main.routing.websocket_urlpatterns)
    ),
    "http": URLRouter(
        main.routing.http_urlpatterns + [re_path(r"", AsgiHandler)]
    ),
})
