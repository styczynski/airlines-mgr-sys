from django.conf.urls import url
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
  url(r'^login/$', auth_views.login, name='login'),
  url(r'^logout/$', auth_views.logout, {'next_page': 'flights'}, name='logout'),
  path('', views.index, name='index'),
  path('planes', views.planes, name='planes'),
  path('flights', views.flights, name='flights'),
  path('users', views.users, name='users'),
  path('flight-edit', views.flightEdit, name='flightEdit'),
  path('data-generator', views.dataGenerator, name='dataGenerator'),
  path('admin-popup', views.adminPopup, name='adminPopup'),
  path('flight-cancel-user-flight', views.cancelUserFlight, name='cancelUserFlight'),
  path('flight-add-user-flight', views.addUserFlight, name='addUserFlight'),
  path('data-generator-popup', views.dataGeneratorPopup, name='dataGeneratorPopup'),
]

urlpatterns += staticfiles_urlpatterns()