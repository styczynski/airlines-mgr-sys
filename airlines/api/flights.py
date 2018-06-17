from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import generics
from django.db import transaction
from rest_framework.exceptions import APIException
import datetime

from .planes import PlaneSerializer
from .crews import CrewSerializer


class TimestampField(serializers.ReadOnlyField):
    def to_representation(self, value):
        timestamp = (value - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)) / datetime.timedelta(
            seconds=1)
        timestamp = int(timestamp)
        return timestamp


class FlightSerializer(serializers.ModelSerializer):
    departure = TimestampField(source='start')
    arrival = TimestampField(source='end')
    plane = PlaneSerializer()
    crew = CrewSerializer()

    class Meta:
        model = Flight
        fields = ['id', 'src', 'dest', 'departure', 'arrival', 'plane', 'tickets', 'crew']


class FlightBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['id', 'plane', 'tickets', 'crew']


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

        if self.request.query_params.get('from'):
            date_start = self.request.query_params.get('from')
        if self.request.query_params.get('to'):
            date_end = self.request.query_params.get('to')

        flights = Flight.objects.all()
        if date_start:
            flights = flights.filter(start__date__gte=date_start)
        if date_end:
            flights = flights.filter(end__date__lte=date_end)

        flights.order_by('start')

        return flights


class InvalidCrewSchedule(APIException):
    status_code = 503
    default_detail = 'Invalid crew schedule was specified.'
    default_code = 'invalid_crew_schedule'


class FlightPartialUpdate(viewsets.ModelViewSet, UpdateModelMixin):
    queryset = Flight.objects.all()
    serializer_class = FlightBaseSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        print(request.data)
        print(kwargs)

        new_flight = Flight.objects.get(pk=kwargs['pk'])
        crew = Crew.objects.get(pk=request.data['crew'])

        crew_flights = crew.flight_set.all()
        crew_flights_times = []
        for flight in crew_flights:
            crew_flights_times.append({
                'start': flight.start,
                'end': flight.end,
                'flight': flight
            })

        crew_flights_times.append({
            'start': new_flight.start,
            'end': new_flight.end,
            'flight': new_flight
        })

        crew_flights_times.sort(key=lambda f: f['start'], reverse=False)
        if len(crew_flights_times) > 0:

            last_end = crew_flights_times[0]['end']
            last_flight = None
            first_flight = True

            for flight_time in crew_flights_times:
                invalid_date = False
                if not first_flight:
                    if flight_time['start'] < last_end:
                        invalid_date = True
                if invalid_date:
                    if last_flight:
                        flight_spec = last_flight['flight'].plane.reg_id + ' and ' + flight_time[
                            'flight'].plane.reg_id + '\n(' + str(last_flight['end']) + ')'
                        raise InvalidCrewSchedule(
                            'Invalid crew schedule was specified:\ntwo flights with colliding dates: ' + flight_spec)
                    raise InvalidCrewSchedule('Invalid crew schedule was specified: two flights with colliding dates')
                last_end = flight_time['end']
                first_flight = False
                last_flight = flight_time

        return super(FlightPartialUpdate, self).update(request, *args, **kwargs)
