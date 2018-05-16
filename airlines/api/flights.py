from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import generics
import datetime

from .planes import PlaneSerializer
from .crews import CrewSerializer


class TimestampField(serializers.ReadOnlyField):
  def to_representation(self, value):
    timestamp = (value - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)) / datetime.timedelta(seconds=1)
    timestamp = int(timestamp)
    return timestamp

class FlightSerializer(serializers.ModelSerializer):
  departure = TimestampField(source='start')
  arrival = TimestampField(source='end')
  plane = PlaneSerializer()
  crew = CrewSerializer()
  
  class Meta:
    model = Flight
    fields = [ 'id', 'src', 'dest', 'departure', 'arrival', 'plane', 'tickets', 'crew' ]

class FlightBaseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Flight
    fields = [ 'id', 'plane', 'tickets', 'crew' ]
    
class FlightViewSet(viewsets.ModelViewSet):
  queryset = Flight.objects.all()
  serializer_class = FlightSerializer
  
class FlightList(viewsets.ModelViewSet):
    serializer_class = FlightSerializer

    def get_queryset(self):
      date_start = None
      date_end = None
      if 'date_start' in self.kwargs:
        date_start = self.kwargs['date_start']
      if 'date_end' in self.kwargs:
        date_end = self.kwargs['date_end']
      if 'date_day' in self.kwargs:
        date_start = self.kwargs['date_day']
        date_end = self.kwargs['date_day']
      
      flights = Flight.objects.all()
      if date_start:
        flights = flights.filter(start__gte=date_start)
      if date_end:
        flights.filter(end__lte=date_end)
        
      return flights
      
class FlightPartialUpdate(viewsets.ModelViewSet, UpdateModelMixin):
  queryset = Flight.objects.all()
  serializer_class = FlightBaseSerializer

  def put(self, request, *args, **kwargs):
    return self.partial_update(request, *args, **kwargs)
      