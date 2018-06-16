#
# Django models for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from django.core.exceptions import ValidationError
from django.db import models

def validatePlaneSchedule(plane):
    flightsDayCount = {}

    flights = plane.flight_set.all()
    for flight in flights:
        dayStr = flight.start.strftime("%d/%m/%y")
        if not dayStr in flightsDayCount:
            flightsDayCount[dayStr] = 1
        else:
            flightsDayCount[dayStr] = flightsDayCount[dayStr] + 1
        for anotherFlight in flights:
            if flight != anotherFlight:
                if flight.start <= anotherFlight.start and flight.end >= anotherFlight.end:
                    raise ValidationError(
                        'Conflighting flight times for plane: ' + str(flight) + ' and ' + str(anotherFlight))

    for flight in flights:
        dayStr = flight.start.strftime("%d/%m/%y")
        if flightsDayCount[dayStr] > 4:
            raise ValidationError('Plane ' + str(plane) + ' makes ' + str(flightsDayCount[
                dayStr]) + ' flights on ' + dayStr + ' and this value should be <= 4')

def validateCrewSchedule(crew):
    flights = crew.flight_set.all()
    for flight in flights:
        dayStr = flight.start.strftime("%d/%m/%y")
        for anotherFlight in flights:
            if flight != anotherFlight:
                if flight.start <= anotherFlight.start and flight.end >= anotherFlight.end:
                    raise ValidationError(
                        'Conflighting flight times for crew: ' + str(flight) + ' and ' + str(anotherFlight))


#
# Model for planes
# Additional contraints:
#   * Maximally 4 flight per day per plane
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
        if self.seats_count < 20:
            raise ValidationError('Plane no. of seats should be >= 20')
        if len(self.reg_id) <= 0:
            raise ValidationError('Plane registration cannot be empty')
        validatePlaneSchedule(self)


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
        if len(self.name) <= 0:
            raise ValidationError('User name should contain at least one character')
        if len(self.surname) <= 0:
           raise ValidationError('User surname should contain at least one character')


#
# Model for crew teams
# Additional contraints:
#   * Non-empty crew identificator
#
class Crew(models.Model):
    capitain = models.OneToOneField('Worker', on_delete=models.CASCADE, null=False, related_name='managed_crew')

    def __str__(self):
        return 'Crew ' + str(self.capitain.getFullName())

    #def clean(self):
    #    if len(self.crew_id) <= 0:
    #        raise ValidationError('Crew ID should contain at least one character')
    #    validateCrewSchedule(self)

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
        if len(self.src) < 3:
            raise ValidationError('Source airport name should contain at least three characters')
        if len(self.dest) < 3:
            raise ValidationError('Destination airport name should contain at least three characters')
        if self.src == self.dest:
            raise ValidationError('Flight source and destination are the same')
        if self.end < self.start:
            raise ValidationError('Invalid flight time. The flight cannot end before starting')
        if (self.end - self.start).total_seconds() / 60.0 <= 30:
            raise ValidationError('Invalid flight time. The flight cannot be shorter than 30 minutes')
        if self.id:
            if self.tickets.count() > self.plane.seats_count:
                raise ValidationError('Could not sell ' + str(self.tickets.count()) + ' tickets for a plane with ' + str(
                    self.plane.seats_count) + ' seats')
        validatePlaneSchedule(self.plane)
        validateCrewSchedule(self.crew)

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
        if len(self.name) <= 0:
            raise ValidationError('Worker name should contain at least one character')
        if len(self.surname) <= 0:
            raise ValidationError('Worker surname should contain at least one character')

class ServerStatusChannels(models.Model):
    name = models.CharField('Channel name', max_length=100)

    def __str__(self):
        return 'Channel '+self.name