#
# Django consumers configuration for airlines management sysyem
#
# This is the configuration for Django channels used for server real-time status reporting.
#
# MIT Piotr Styczyński 2018
#
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from django.db import transaction
from channels.generic.websocket import WebsocketConsumer
import json
import time

#
# Delcare a consumer for server real-time status information
#
class ServerStatsConsumer(WebsocketConsumer):

    def connect(self):
        (self.accept)()
        from .models import ServerStatusChannels
        with transaction.atomic():
            allChannels = ServerStatusChannels.objects.all()
            allChannels._result_cache = None
            allChannels.count()
            allChannels.delete()
            ServerStatusChannels.objects.create(name=self.channel_name)

    def server_status_message(self, event):
        try:
            message = event['message']
            mode = event['mode']
            (self.send)(text_data=json.dumps({
                'type': 'server_status_message',
                'server_mode': mode,
                'server_status': message
            }))
        except:
            return;


#
#
# ServerStatusChannels.objects.create(name=self.channel_name)
#
#