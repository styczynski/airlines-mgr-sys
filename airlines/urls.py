from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('planes', views.planes, name='planes'),
  path('flights', views.flights, name='flights'),
  path('users', views.users, name='users'),
  path('flight-edit', views.flightEdit, name='flightEdit'),
  path('data-generator', views.dataGenerator, name='dataGenerator'),
  path('admin-popup', views.adminPopup, name='adminPopup'),
  path('data-generator-popup', views.dataGeneratorPopup, name='dataGeneratorPopup'),
]

urlpatterns += staticfiles_urlpatterns()