from django.apps import AppConfig
from .routing import websocket_urlpatterns

class AirlinesConfig(AppConfig):
  name = 'airlines'

class Routing():
  urlpatterns = websocket_urlpatterns
  