from django.utils import timezone
from random import randint
import random
import string
import datetime

airports = [
  'Warsaw',
  'Amsterdam',
  'Gdańsk',
  'Radom',
  'Berlin',
  'Paris',
  'New York',
  'Sydney',
  'Boston',
  'Washington DC',
  'New Orlean',
  'Rome',
  'London',
  'Yrkuck',
  'Los Angeles',
  'Tokio',
  'Bern'
]

names = [
  'Adam',
  'Małgorzata',
  'Jan',
  'Piotr',
  'Zbigniew',
  'Agata',
  'Paulina',
  'Marysia',
  'Aleksandra',
  'Aleksander',
  'Michał',
  'Sebastian',
  'Jerzy',
  'Małgorzata',
  'Emil',
  'Eustachy',
  'Kamil',
  'Krystyna',
  'Emilia',
  'Hania',
  'Przemysław',
  'Tomasz',
  'Kuba',
  'Irmina',
  'Grażyna',
  'Karolina',
  'Ryszarda',
  'Michalina'
]

surnames = [
  'Kowalski',
  'Kowalczyk',
  'Śmigły',
  'Koc',
  'Kot',
  'Jurkiewicz',
  'Zbyszkiewicz',
  'Rytter',
  'Tomasiewicz',
  'Staśkiewicz',
  'Kiewicz',
  'Źdźbło',
  'Ukleya',
  'Macer',
  'Spychewicz',
  'Śpiszkiewicz',
  'Bąk',
  'Bęc',
  'Julewicz',
  'Pomac',
  'Jakubowicz',
  'Rekta',
  'Kubica',
  'Stonka',
  'Bukiet',
  'Lepić',
  'Tomczyk',
  'Więc',
  'Wąs',
  'Ukracz',
  'Rela',
  'Ręka',
  'Pan',
  'Panek',
  'Lubicz',
  'Dostojewski',
  'Wędrychowicz',
  'Balcerowicz',
  'Makaronowicz',
  'Tytło',
  'Gaźdź',
  'Grącek',
  'Gacek',
  'Śpiący',
  'Aleja',
  'Bigos',
  'Mop',
  'Krata',
  'Kratowicz',
  'Fajnek',
  'Jełowicz',
  'Tysak',
  'Konik',
  'Rzęsa'
]

def generateFlight(plane, Flight, flight_current_end):
  global airports
  src = airports[randint(0, len(airports)-1)]
  dest = airports[randint(0, len(airports)-1)]
  while src == dest:
    dest = airports[randint(0, len(airports)-1)]
    
  minutes = randint(30, 60*3)
  delay = randint(40, 60)
  start = flight_current_end + datetime.timedelta(minutes=delay)
  end = start + datetime.timedelta(minutes=minutes)
  return {
    'flight': Flight(src=src, dest=dest, start=start, end=end, plane=plane),
    'end': end
  }
  
def generateUserData():
  surname = surnames[randint(0, len(surnames)-1)]
  name = names[randint(0, len(names)-1)]
  return {
    'surname': surname,
    'name': name,
    'flights': []
  }
  
def generateUser(user_data, User):
  user = User(surname=user_data['surname'], name=user_data['name'])
  user.save()
  user.flights.set(user_data['flights'])
  user.save()
  return user
  
def generateFlightSubscriptions(flight, user_samples):
  seats_min = 0
  seats_max = flight.plane.seats_count
  subscr_seats = randint(seats_min, seats_max)
  set_ids = {}
  for i in range(subscr_seats):
    userid = randint(0, len(user_samples)-1)
    while userid in set_ids:
      userid = randint(0, len(user_samples)-1)
    set_ids[userid] = 'set'
    user_samples[userid]['flights'].append(flight)
  return user_samples

def PlanesGenerator(Plane, Flight, User, form):

  User.objects.all().delete()
  Flight.objects.all().delete()
  Plane.objects.all().delete()

  input = form.cleaned_data
  planes_data = []
  flights_data = []
  
  users_count = int(input['users_count'])
  planes_count = int(input['planes_count'])
  plane_seats_count_min = int(input['plane_seats_count_min'])
  plane_seats_count_max = int(input['plane_seats_count_max'])
  plane_flights_count_min = int(input['plane_flights_count_min'])
  plane_flights_count_max = int(input['plane_flights_count_max'])
  plane_reg_format = str(input['plane_reg_format'])
  
  seats_samples = []
  seats_samples_count = randint(planes_count//4, planes_count//3) + 4
  for i in range(seats_samples_count):
    value = randint(plane_seats_count_min, plane_seats_count_max)
    valueMod = ( value // 10 ) * 10
    if valueMod >= plane_seats_count_min and valueMod <= plane_seats_count_max:
      value = valueMod
    seats_samples.append(value)
    
  user_samples = []
  for i in range(users_count):
    user_samples.append(generateUserData())
  
  times_samples = []
  times_samples_count = randint(planes_count//4, planes_count//3) + 4
  for i in range(times_samples_count):
    times_samples.append(randint(2, 2700))
  
  for plane_index in range(planes_count):
    reg_id = ''
    seats_count = seats_samples[randint(0, seats_samples_count-1)]
    time_days = times_samples[randint(0, times_samples_count-1)]
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
    plane.save()
    
    flight_current_end = timezone.now()
    for flight_index in range(randint(plane_flights_count_min, plane_flights_count_max)):
      flight = generateFlight(plane, Flight, flight_current_end)
      flights_data.append(flight['flight'])
      flight_current_end = flight['end']
      flight['flight'].save()
      user_samples = generateFlightSubscriptions(flight['flight'], user_samples)
    
  users_data = []
  for i in range(users_count):
    users_data.append(generateUser(user_samples[i], User))
    
    #data.append(reg_id)
  return {
    'planes': planes_data,
    'flights': flights_data,
    'users': users_data
  }