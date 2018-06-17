#
# Application URLs declarations for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from django.conf.urls import url, include
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

from . import views
from . import api
from . import rendering

urlpatterns = [
    url(r'api/', include(api.createRouter().urls)),
    #url(r'api-auth/', include('rest_framework.urls')),
    url(r'login/', auth_views.login, name='login'),
    url(r'logout/', auth_views.logout, {'next_page': 'flights'}, name='logout'),
    path(r'', views.index, name='index'),
    path(r'tests/', views.tests, name='tests'),
    path(r'tests-run/', views.testsRun, name='tests-run'),
    path(r'planes/', views.planes, name='planes'),
    path(r'flights/', views.flights, name='flights'),
    path(r'users/', views.users, name='users'),
    path(r'crews-panel/', views.crewsPanel, name='crewsPanel'),
    path(r'crews-panel/list/', views.crews, name='crews'),
    path(r'crews-panel/assign/', views.crewsPanel, name='crewsPanel'),
    path(r'workers/', views.workers, name='workers'),
    path(r'flight-edit/', views.flightEdit, name='flightEdit'),
    path(r'data-generator/', views.dataGenerator, name='dataGenerator'),
    path(r'admin-popup/', views.adminPopup, name='adminPopup'),
    path(r'flight-cancel-user-flight/', views.cancelUserFlight, name='cancelUserFlight'),
    path(r'flight-add-user-flight/', views.addUserFlight, name='addUserFlight'),
    path(r'data-generator-popup/', views.dataGeneratorPopup, name='dataGeneratorPopup'),
    path(r'server-status/', views.serverStatus, name='serverStatus')
]

urlpatterns += staticfiles_urlpatterns()
