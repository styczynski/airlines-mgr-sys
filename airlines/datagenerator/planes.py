from django.utils import timezone
from random import randint
import random
import string
import datetime
from django.db import transaction
from itertools import zip_longest
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .data_airports import *
from .data_names import *
from .data_surnames import *

disableSockets = False
lastProgress = 0


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def save_list(objDescription, objList, max_count_per_save=100):
    chunks_count = len(objList) // max_count_per_save
    chunks_i = 0
    progressThreshold = chunks_count / 20 + 1
    for objChunk in grouper(objList, max_count_per_save, None):
        chunks_i = chunks_i + 1
        printProgress('Saving ' + str(objDescription), chunks_i, chunks_count, progressThreshold=progressThreshold)
        with transaction.atomic():
            for obj in objChunk:
                if obj:
                    obj.save()


def printProgress(task, current, maximum, progressThreshold=1):

    global lastProgress
    global disableSockets

    if current >= lastProgress - progressThreshold and current <= lastProgress + progressThreshold:
        return True

    lastProgress = current

    if maximum <= 0:
        maximum = 1
    print('[DataGenerator] ' + str(task) + ' ' + str(((current / maximum * 10000) // 10) / 10) + '%')

    if not disableSockets:
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            'server_status_listeners',
            {
                'type': 'server_status_message',
                'message': {
                    'task_name': str(task),
                    'task_progress': str(((current / maximum * 10000) // 10) / 10) + '%'
                },
                'mode': 'progress'
            }
        )


def printProgressEnd(obj):
    global disableSockets

    planes_count = len(obj['planes'])
    flights_count = len(obj['flights'])
    users_count = len(obj['users'])

    print('[DataGenerator] Submitting results.')
    if not disableSockets:
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'server_status_listeners',
                {
                    'type': 'server_status_message',
                    'message': 'Generated ' + str(planes_count) + ' plane/-s, ' + str(
                        flights_count) + ' flight/-s and ' + str(users_count) + ' user/-s',
                    'mode': 'progress_end'
                }
            )
        except:
            disableSockets = True
            return False
        return True


def generateFlight(plane, Flight, last_flight_status, plane_flights_count_per_day):
    global airports
    src = airports[randint(0, len(airports) - 1)]
    dest = airports[randint(0, len(airports) - 1)]
    while src == dest:
        dest = airports[randint(0, len(airports) - 1)]

    if not last_flight_status:
        last_flight_status = {}
    if not 'end' in last_flight_status:
        last_flight_status['end'] = timezone.now()
    if not 'day_count' in last_flight_status:
        last_flight_status['day_count'] = 0

    minutes = randint(30, 60 * 3)
    delay = randint(40, 60)
    start = last_flight_status['end'] + datetime.timedelta(minutes=delay)
    end = start + datetime.timedelta(minutes=minutes)
    day_count = last_flight_status['day_count'] + 1

    if end.weekday() != last_flight_status['end'].weekday():
        day_count = 1

    if day_count > plane_flights_count_per_day:
        day_count = day_count - 1
        while True:
            delay = delay + randint(40, 60)
            start = last_flight_status['end'] + datetime.timedelta(minutes=delay)
            end = start + datetime.timedelta(minutes=minutes)
            if end.weekday() != last_flight_status['end'].weekday():
                break
        day_count = 1

    return {
        'flight': Flight(src=src, dest=dest, start=start, end=end, plane=plane),
        'start': start,
        'end': end,
        'day_count': day_count
    }


def generateUserData():
    surname = surnames[randint(0, len(surnames) - 1)]
    name = names[randint(0, len(names) - 1)]
    return {
        'surname': surname,
        'name': name,
        'flights': []
    }


def generateWorkerData(worker_data, worker_names_table):
    worker_name = worker_data['surname'] + '|' + worker_data['name']
    if worker_name in worker_names_table:
        return None

    # worker = Worker(surname=worker_data['surname'], name=worker_data['name'])
    worker_names_table[worker_name] = True
    # worker_data['worker'] = worker
    # return {
    #  'worker_obj': worker,
    #  'worker_data': worker_data
    # }

    return {
        'name': worker_data['name'],
        'surname': worker_data['surname'],
        'crew': None
    }


def generateCrew(workers_data, Crew, crew_table):
    pilot_user = workers_data[randint(0, len(workers_data) - 1)]
    if pilot_user:
        if pilot_user['crew'] != None:
            return None
    else:
        return None

    crew_name = pilot_user['name'] + ' ' + pilot_user['surname']

    crew = Crew(crew_id=crew_name)
    pilot_user['crew'] = crew
    return crew


def crewCompleteWorkers(workers_data, crew):
    requested_workers = randint(0, 10)

    for worker in workers_data:
        if worker:
            if worker['crew'] == None:
                requested_workers = requested_workers - 1
                worker['crew'] = crew
                if requested_workers <= 0:
                    return


def generateWorkersFromData(workers_data, Worker):
    workers = []
    for data in workers_data:
        worker = Worker(name=data['name'], surname=data['surname'], crew=data['crew'])
        workers.append(worker)
    return workers


def generateUser(user_data, User, user_names_table):
    user_name = user_data['surname'] + '|' + user_data['name']
    if user_name in user_names_table:
        return None

    user = User(surname=user_data['surname'], name=user_data['name'])
    # user.save()
    # user.flights.set(user_data['flights'])
    # user.save()
    user_names_table[user_name] = True
    user_data['user'] = user
    return {
        'user_obj': user,
        'user_data': user_data
    }


def userInheritFlights(user_data):
    if user_data['user']:
        user_data['user'].flights.set(user_data['flights'])


def generateFlightSubscriptions(flight, user_samples):
    seats_min = 0
    seats_max = flight.plane.seats_count
    subscr_seats = randint(seats_min, seats_max)
    set_ids = {}
    tries = 0
    for i in range(subscr_seats):
        userid = randint(0, len(user_samples) - 1)
        tries = 0
        while userid in set_ids:
            userid = randint(0, len(user_samples) - 1)
            tries = tries + 1
            if tries > 30:
                return user_samples
        set_ids[userid] = 'set'
        user_samples[userid]['flights'].append(flight)
    return user_samples


def assignCrewsToFlights(flights_data, crews_objs):
    flights_data.sort(key=lambda f: f.start, reverse=False)

    crew_no = 0
    crew_count = len(crews_objs)
    for crew in crews_objs:
        crew_no = crew_no + 1
        printProgress('Assigning crews to flights', crew_no, crew_count, progressThreshold=50)
        crew_current_end = None
        for flight in flights_data:
            should_add = False
            try:
                if not flight.crew:
                    if not crew_current_end:
                        should_add = True
                    else:
                        if flight.start > crew_current_end:
                            should_add = True
            except:
                if not crew_current_end:
                    should_add = True
                else:
                    if flight.start > crew_current_end:
                        should_add = True
            if should_add:
                flight.crew = crew
                crew_current_end = flight.end


def PlanesGenerator(Plane, Flight, User, Worker, Crew, form_data):
    with transaction.atomic():
        User.objects.all().delete()
        Flight.objects.all().delete()
        Plane.objects.all().delete()
        Worker.objects.all().delete()
        Crew.objects.all().delete()

    input = form_data
    planes_data = []
    flights_data = []
    generated_planes = []
    generated_flights = []

    seats_samples = []
    seats_samples_count = 0
    user_samples = []
    worker_samples = []
    times_samples = []
    times_samples_count = 0

    users_count = int(input['users_count'])
    planes_count = int(input['planes_count'])
    plane_seats_count_min = int(input['plane_seats_count_min'])
    plane_seats_count_max = int(input['plane_seats_count_max'])
    plane_flights_count_min = int(input['plane_flights_count_min'])
    plane_flights_count_max = int(input['plane_flights_count_max'])
    plane_flights_count_per_day = int(input['plane_flights_count_per_day'])
    plane_reg_format = str(input['plane_reg_format'])

    # with transaction.atomic():

    print('Generate seats samples')

    seats_samples_count = randint(planes_count // 4, planes_count // 3) + 4
    for i in range(seats_samples_count):
        value = randint(plane_seats_count_min, plane_seats_count_max)
        valueMod = (value // 10) * 10
        if valueMod >= plane_seats_count_min and valueMod <= plane_seats_count_max:
            value = valueMod
        seats_samples.append(value)

    print('Generate user samples')

    for i in range(users_count):
        user_samples.append(generateUserData())

    print('Generate times samples')

    times_samples_count = randint(planes_count // 4, planes_count // 3) + 4
    for i in range(times_samples_count):
        times_samples.append(randint(2, 2700))

    print('Start generating planes')

    for plane_index in range(planes_count):
        printProgress('Generating planes', plane_index + 1, planes_count, progressThreshold=100)

        reg_id = ''
        seats_count = seats_samples[randint(0, seats_samples_count - 1)]
        time_days = times_samples[randint(0, times_samples_count - 1)]
        service_start = timezone.now() - datetime.timedelta(days=time_days)
        for c in plane_reg_format:
            if c == '.':
                reg_id += random.choice(string.punctuation + string.ascii_letters + string.digits)
            elif c == 'C':
                reg_id += random.choice(string.ascii_letters).upper()
            elif c == 'N':
                reg_id += random.choice(string.digits)
            else:
                reg_id += c

        plane = Plane(reg_id=reg_id, seats_count=seats_count, service_start=service_start)
        planes_data.append(plane)
        generated_planes.append(plane)

    save_list('planes', generated_planes)

    for plane_index in range(planes_count):
        printProgress('Generating subscriptions', plane_index + 1, planes_count, progressThreshold=100)

        plane = generated_planes[plane_index]
        last_flight_status = {}
        subscription_count = randint(plane_flights_count_min, plane_flights_count_max)
        for flight_index in range(subscription_count):
            flight = generateFlight(plane, Flight, last_flight_status, plane_flights_count_per_day)
            flights_data.append(flight['flight'])
            last_flight_status = flight
            # flight['flight'].save()
            generated_flights.append(flight['flight'])
            user_samples = generateFlightSubscriptions(flight['flight'], user_samples)

    print('Generate workers samples')

    workers_count = (len(flights_data) // 4 + 2) * 10

    for i in range(workers_count):
        worker_samples.append(generateUserData())

    print('Start generaing workers')

    workers_data = []
    worker_objs = []
    worker_names_table = {}
    for i in range(workers_count):
        printProgress('Generating workers', i + 1, workers_count, progressThreshold=50)
        workerData = generateWorkerData(worker_samples[i], worker_names_table)
        if workerData:
            workers_data.append(workerData);
            # workers_objs.append(workerGen['worker_obj'])

    print('Start generating crews')

    crews_table = {}
    crews_objs = []
    crews_count = len(flights_data)
    for i in range(crews_count):
        printProgress('Generating workers', i + 1, crews_count, progressThreshold=50)
        crewGen = generateCrew(workers_data, Crew, crews_table)
        if crewGen:
            crews_objs.append(crewGen)

    for crewGen in crews_objs:
        crewCompleteWorkers(workers_data, crewGen)

    for worker in workers_data:
        if not worker['crew']:
            worker['crew'] = crews_objs[randint(0, len(crews_objs) - 1)]

    save_list('crews', crews_objs)

    workers_objs = generateWorkersFromData(workers_data, Worker);

    print('Assign crews to flights')

    assignCrewsToFlights(flights_data, crews_objs)

    save_list('flights', generated_flights)

    print('Generate users')
    users_data = []
    users_objs = []
    user_names_table = {}
    for i in range(users_count):
        printProgress('Generating users', i + 1, users_count, progressThreshold=1000)
        userGen = generateUser(user_samples[i], User, user_names_table)
        if userGen:
            users_objs.append(userGen['user_obj'])
            users_data.append(userGen['user_data'])

    save_list('users', users_objs)
    save_list('workers', workers_objs)

    users_data_len = len(users_data)
    with transaction.atomic():
        for i in range(users_data_len):
            printProgress('Matching users with flights', i + 1, users_data_len, progressThreshold=25)
            userInheritFlights(users_data[i])

    save_list('users with flights', users_objs)

    obj = {
        'planes': planes_data,
        'flights': flights_data,
        'users': users_data
    }

    printProgressEnd(obj)
    return obj
