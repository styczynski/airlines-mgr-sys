from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets

from .workers import WorkerViewSet
from .crews import CrewList
from .flights import FlightViewSet, FlightList, FlightPartialUpdate
from .planes import PlaneViewSet
from .auth import AuthViewSet


def createRouter():
  router = routers.DefaultRouter()
  router.register(r'workers', WorkerViewSet)
  router.register(r'crews', CrewList, base_name='crews/')
  router.register(r'crews/search/(?P<crew_name>.+)', CrewList, base_name='crews/search/')
  router.register(r'planes', PlaneViewSet)
  router.register(r'flights', FlightList, base_name='flights')
  router.register(r'flights/by-date/start/(?P<date_start>.+)', FlightList, base_name='flights/by-date/')
  router.register(r'flights/by-date/end/(?P<date_end>.+)', FlightList, base_name='flights/by-date/')
  router.register(r'flights/by-date/(?P<date_start>.+)', FlightList, base_name='flights/by-date/')
  router.register(r'flights/by-date/(?P<date_start>.+)/(?P<date_end>.+)', FlightList, base_name='flights/by-date/')
  router.register(r'flights/day/(?P<date_day>.+)', FlightList, base_name='flights/day/')
  router.register(r'flights/update', FlightPartialUpdate, base_name='flights/update/')
  router.register(r'check-auth', AuthViewSet, base_name='check-auth/')
  return router
