#
# Django models for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from django.db import models

from . import validator

#
# Model for planes
# Additional contraints:
#   * Seats count >= 20
#   * Non-empty registration identificator
#
class Plane(models.Model):
    reg_id = models.CharField('Registration identificator', max_length=200, unique=True)
    seats_count = models.IntegerField('Seats')
    service_start = models.DateTimeField('In service since')

    def __str__(self):
        return 'Plane ' + self.reg_id

    def clean(self):
        validator.validatePlane(self)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Plane, self).save(*args, **kwargs)

#
# Model for users
# Additional contraints:
#   * Non-empty name and surname
#
class User(models.Model):
    surname = models.CharField('Surname', max_length=100)
    name = models.CharField('Name', max_length=100)
    flights = models.ManyToManyField('Flight', blank=True)

    class Meta:
        unique_together = ('surname', 'name',)

    def __str__(self):
        return 'User ' + self.surname + ' ' + self.name

    def clean(self):
        validator.validateUser(self)

    def save(self, *args, **kwargs):
        self.clean()
        return super(User, self).save(*args, **kwargs)

#
# Model for crew teams
# Additional contraints:
#   * Non-empty crew identificator
#
class Crew(models.Model):
    capitain = models.OneToOneField('Worker', on_delete=models.CASCADE, null=False, related_name='managed_crew')

    def __str__(self):
        return 'Crew ' + str(self.capitain.getFullName())

    def clean(self):
        validator.validateCrew(self)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Crew, self).save(*args, **kwargs)

#
# Model for flights
# Additional contraints:
#   * Source and destination have at least 3 characters
#   * Source and destination are not equal
#   * Flight should end at least 30 minutes after start
#   * Total number of sold tickets for a flight could not exceed its plane seats count
#
class Flight(models.Model):
    src = models.CharField('Source airport', max_length=200)
    dest = models.CharField('Destination airport', max_length=200)
    start = models.DateTimeField('Start date')
    end = models.DateTimeField('Landing date')
    plane = models.ForeignKey(Plane, on_delete=models.PROTECT, null=False)
    tickets = models.ManyToManyField('User', through=User.flights.through, blank=True)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return 'Flight ' + self.src + ' -> ' + self.dest

    def clean(self):
        validator.validateFlight(self)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Flight, self).save(*args, **kwargs)
#
# Model for workers
# Additional contraints:
#   * Non-empty name and surname
#
class Worker(models.Model):
    surname = models.CharField('Surname', max_length=100)
    name = models.CharField('Name', max_length=100)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('surname', 'name',)

    def getFullName(self):
        return self.surname + ' ' + self.name

    def __str__(self):
        return 'Worker ' + self.surname + ' ' + self.name

    def clean(self):
        validator.validateWorker(self)

    def save(self, *args, **kwargs):
        self.clean()
        return super(Worker, self).save(*args, **kwargs)
#
# Model for saving websocket connections for Django Channels
# Additional contraints:
#   * Non-empty name
#
class ServerStatusChannels(models.Model):
    name = models.CharField('Channel name', max_length=100)

    def __str__(self):
        return 'Channel '+self.name

    def clean(self):
        validator.validateServerStatusChannels(self)

    def save(self, *args, **kwargs):
        self.clean()
        return super(ServerStatusChannels, self).save(*args, **kwargs)