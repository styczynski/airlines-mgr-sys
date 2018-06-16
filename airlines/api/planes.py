from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets
import datetime


class TimestampField(serializers.ReadOnlyField):
    def to_representation(self, value):
        timestamp = (value - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)) / datetime.timedelta(
            seconds=1)
        timestamp = int(timestamp)
        return timestamp


class PlaneSerializer(serializers.ModelSerializer):
    service_since = TimestampField(source='service_start')

    class Meta:
        model = Plane
        fields = ['reg_id', 'seats_count', 'service_since']


class PlaneViewSet(viewsets.ModelViewSet):
    queryset = Plane.objects.all()
    serializer_class = PlaneSerializer
