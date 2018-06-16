#
# Django routing file for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'server-status', consumers.ServerStatsConsumer),
]

main_channel_consumer = consumers.ServerStatsConsumer