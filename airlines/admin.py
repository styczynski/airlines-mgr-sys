#
# Django admin file for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from django.contrib import admin

from .models import Plane, Flight, User, Worker, Crew

admin.site.register(Plane)
admin.site.register(Flight)
admin.site.register(User)
admin.site.register(Worker)
admin.site.register(Crew)
