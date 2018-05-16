from django.conf.urls import url, include
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views


from . import views
from . import api
from . import rendering

urlpatterns = [
  url(r'^api/', include(api.createRouter().urls)),
  url(r'^api-auth/', include('rest_framework.urls')),
  url(r'^login/$', auth_views.login, name='login'),
  url(r'^logout/$', auth_views.logout, {'next_page': 'flights'}, name='logout'),
  path('', views.index, name='index'),
  path('planes', views.planes, name='planes'),
  path('flights', views.flights, name='flights'),
  path('users', views.users, name='users'),
  path('crews', views.crews, name='crews'),
  path('workers', views.workers, name='workers'),
  path('crews-panel', views.crewsPanel, name='crewsPanel'),
  path('flight-edit', views.flightEdit, name='flightEdit'),
  path('data-generator', views.dataGenerator, name='dataGenerator'),
  path('admin-popup', views.adminPopup, name='adminPopup'),
  path('flight-cancel-user-flight', views.cancelUserFlight, name='cancelUserFlight'),
  path('flight-add-user-flight', views.addUserFlight, name='addUserFlight'),
  path('data-generator-popup', views.dataGeneratorPopup, name='dataGeneratorPopup'),
  path('server-status', views.serverStatus, name='serverStatus')
]

urlpatterns += staticfiles_urlpatterns()


rendering.generateStaticPages()