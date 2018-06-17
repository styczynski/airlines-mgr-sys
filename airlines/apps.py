#
# Django apps file for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from django.apps import AppConfig
from .routing import websocket_urlpatterns


class AirlinesConfig(AppConfig):
    name = 'airlines'


class Routing():
    urlpatterns = websocket_urlpatterns
