from django.core.exceptions import ValidationError

def validatePlaneSchedule(plane, newFlight=None):
    flightsDayCount = {}

    flights = plane.flight_set.all()

    if newFlight:
        flights = list(flights)
        flights.extend([ newFlight ])

    for flight in flights:
        dayStr = flight.start.strftime("%d/%m/%y")
        if not dayStr in flightsDayCount:
            flightsDayCount[dayStr] = 1
        else:
            flightsDayCount[dayStr] = flightsDayCount[dayStr] + 1
        for anotherFlight in flights:
            if flight != anotherFlight:
                if (flight.start <= anotherFlight.start and flight.end >= anotherFlight.start) or (flight.start >= anotherFlight.start and flight.start <= anotherFlight.end):
                    raise ValidationError(
                        'Conflighting flight times for plane: ' + str(flight) + ' and ' + str(anotherFlight))

def validateCrewSchedule(crew, newFlight=None):

    flights = crew.flight_set.all()

    if newFlight:
        flights = list(flights)
        flights.extend([ newFlight ])

    for flight in flights:
        for anotherFlight in flights:
            if flight != anotherFlight:
                if (flight.start <= anotherFlight.start and flight.end >= anotherFlight.start) or (flight.start >= anotherFlight.start and flight.start <= anotherFlight.end):
                    raise ValidationError(
                        'Conflighting flight times for crew: ' + str(flight) + ' and ' + str(anotherFlight))

def validatePlane(self):
    if self.seats_count < 20:
        raise ValidationError('Plane no. of seats should be >= 20')
    if len(self.reg_id) <= 0:
        raise ValidationError('Plane registration cannot be empty')
    validatePlaneSchedule(self)

def validateUser(self):
    if len(self.name) <= 0:
        raise ValidationError('User name should contain at least one character')
    if len(self.surname) <= 0:
        raise ValidationError('User surname should contain at least one character')

def validateCrew(self):
    validateCrewSchedule(self)

def validateWorker(self):
    if len(self.name) <= 0:
        raise ValidationError('Worker name should contain at least one character')
    if len(self.surname) <= 0:
        raise ValidationError('Worker surname should contain at least one character')

def validateFlight(self):
    if not hasattr(self, 'crew'):
        raise ValidationError('Every flight must have the crew assigned.')
    if len(self.src) < 3:
        raise ValidationError('Source airport name should contain at least three characters')
    if len(self.dest) < 3:
        raise ValidationError('Destination airport name should contain at least three characters')
    if self.src == self.dest:
        raise ValidationError('Flight source and destination are the same')
    if self.end < self.start:
        raise ValidationError('Invalid flight time. The flight cannot end before starting')
    if (self.end - self.start).total_seconds() / 60.0 < 30:
        raise ValidationError('Invalid flight time. The flight cannot be shorter than 30 minutes ('+str((self.end - self.start).total_seconds() / 60.0)+' mins.)')
    if self.id:
        if self.tickets.count() > self.plane.seats_count:
            raise ValidationError('Could not sell ' + str(self.tickets.count()) + ' tickets for a plane with ' + str(
                self.plane.seats_count) + ' seats')
    validatePlaneSchedule(self.plane, newFlight=self)
    validateCrewSchedule(self.crew, newFlight=self)

def validateServerStatusChannels(self):
    if len(self.name) < 1:
        raise ValidationError('Channel name must have at least one character')