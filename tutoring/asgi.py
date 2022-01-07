"""
ASGI config for tutoring project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from signalingapp import routing
import signalingapp


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutoring.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket" : AuthMiddlewareStack(
        URLRouter(
            signalingapp.routing.websocket_urlpatterns
        )
    )
})
