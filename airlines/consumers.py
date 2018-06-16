#
# Django consumers configuration for airlines management sysyem
#
# This is the configuration for Django channels used for server real-time status reporting.
#
# MIT Piotr Styczyński 2018
#
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


#
# Delcare a consumer for server real-time status information
#
class ServerStatsConsumer(WebsocketConsumer):
    def connect(self):
        try:
            self.user = self.scope["user"]
            if not self.user.is_authenticated:
                self.close()
                return False
            if self.user.is_anonymous:
                self.close()
                return False
            async_to_sync(self.channel_layer.group_add)("server_status_listeners", self.channel_name)
            self.accept()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'server_status_listeners',
                {
                    'type': 'server_status_message',
                    'message': 'hello',
                    'mode': 'init'
                }
            )
        except:
            return;

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)("server_status_listeners", self.channel_name)
        except:
            return;

    def receive(self, text_data):
        return self

    def server_status_message(self, event):
        try:
            message = event['message']
            mode = event['mode']
            self.send(text_data=json.dumps({
                'type': 'server_status_message',
                'server_mode': mode,
                'server_status': message
            }))
        except:
            return;
