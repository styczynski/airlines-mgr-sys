from django.utils import timezone
from random import randint
import random
import string
import datetime
from django.db import transaction
from itertools import zip_longest
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

disableSockets = False

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
  'Bern',
  'Kabul',
  'Tirana',
  'Algiers',
  'Andorra la Vella',
  'Luanda',
  'Saint John\'s',
  'Buenos Aires',
  'Yerevan',
  'Canberra',
  'Vienna',
  'Baku',
  'Nassau',
  'Manama',
  'Dhaka',
  'Bridgetown',
  'Minsk',
  'Brussels',
  'Belmopan',
  'Porto-Novo',
  'Thimphu',
  'Sarajevo',
  'Gaborone',
  'Brasilia',
  'Bandar Seri Begawan',
  'Sofia',
  'Ouagadougou',
  'Bujumbura',
  'Praia',
  'Phnom Penh',
  'Yaounde',
  'Ottawa',
  'Bangui',
  'N\'Djamena',
  'Santiago',
  'Beijing',
  'Bogotá',
  'Moroni',
  'Kinshasa',
  'Brazzaville',
  'San Jose',
  'Yamoussoukro',
  'Zagreb',
  'Havana',
  'Nicosia',
  'Prague',
  'Copenhagen',
  'Roseau',
  'Santo Domingo',
  'Quito',
  'Cairo',
  'San Salvador',
  'Asmara',
  'Tallinn',
  'Addis Ababa',
  'Suva',
  'Helsinki',
  'Paris',
  'Libreville',
  'Banjul',
  'Tbilisi',
  'Berlin',
  'Accra',
  'Athens',
  'Saint George\'s',
  'Guatemala City',
  'Conakry',
  'Bissau',
  'Georgetown',
  'Port-au-Prince',
  'Tegucigalpa',
  'Budapest',
  'Reykjavik',
  'New Delhi',
  'Jakarta',
  'Tehran',
  'Baghdad',
  'Dublin',
  'Jerusalem',
  'Rome',
  'Kingston',
  'Tokyo',
  'Amman',
  'Astana',
  'Nairobi',
  'Tarawa',
  'Pristina',
  'Kuwait City',
  'Bishkek',
  'Vientiane',
  'Riga',
  'Beirut',
  'Maseru',
  'Monrovia',
  'Tripoli',
  'Vaduz',
  'Vilnius',
  'Luxembourg',
  'Abu Dhabi',
  'London',
  'Washington, D.C.',
  'Montevideo',
  'Tashkent',
  'Port Vila',
  'Vatican City',
  'Caracas',
  'Hanoi',
  'Sana\'a',
  'Lusaka',
  'Harare',
  'Seoul',
  'Juba',
  'Madrid',
  'Sri Jayawardenepura Kotte',
  'Khartoum',
  'Paramaribo',
  'Stockholm',
  'Bern',
  'Damascus',
  'Taipei',
  'Dushanbe',
  'Dodoma',
  'Bangkok',
  'Dili',
  'Lomé',
  'Nukuʻalofa',
  'Port of Spain',
  'Tunis',
  'Ankara',
  'Ashgabat',
  'Funafuti',
  'Kampala',
  'Kathmandu',
  'Amsterdam',
  'Wellington',
  'Managua',
  'Niamey',
  'Abuja',
  'Pyongyang',
  'Oslo',
  'Muscat',
  'Islamabad',
  'Ngerulmud',
  'Jerusalem (East)',
  'Panama City',
  'Port Moresby',
  'Asunción',
  'Lima',
  'Manila',
  'Warsaw',
  'Lisbon',
  'Doha',
  'Bucharest',
  'Moscow',
  'Kigali',
  'Basseterre',
  'Castries',
  'Kingstown',
  'Apia',
  'San Marino',
  'São Tomé',
  'Riyadh',
  'Dakar',
  'Belgrade',
  'Victoria',
  'Freetown',
  'Singapore',
  'Bratislava',
  'Ljubljana',
  'Honiara',
  'Mogadishu',
  'Skopje',
  'Antananarivo',
  'Lilongwe',
  'Kuala Lumpur',
  'Male',
  'Bamako',
  'Valletta',
  'Majuro',
  'Nouakchott',
  'Port Louis',
  'Mexico City',
  'Palikir',
  'Chisinau',
  'Monaco',
  'Ulaanbaatar',
  'Podgorica',
  'Rabat',
  'Maputo',
  'Naypyidaw',
  'Windhoek'
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
  'Michalina',
  'Anna',
  'Maria',
  'Katarzyna',
  'Małgorzata',
  'Agnieszka',
  'Krystyna',
  'Barbara',
  'Ewa',
  'Elżbieta',
  'Zofia',
  'Janina',
  'Teresa',
  'Joanna',
  'Magdalena',
  'Monika',
  'Jadwiga',
  'Danuta',
  'Irena',
  'Halina',
  'Helena',
  'Beata',
  'Aleksandra',
  'Marta',
  'Dorota',
  'Marianna',
  'Grażyna',
  'Jolanta',
  'Stanisława',
  'Iwona',
  'Karolina',
  'Bożena',
  'Urszula',
  'Justyna',
  'Renata',
  'Alicja',
  'Paulina',
  'Sylwia',
  'Natalia',
  'Wanda',
  'Agata',
  'Aneta',
  'Izabela',
  'Ewelina',
  'Marzena',
  'Wiesława',
  'Genowefa',
  'Patrycja',
  'Kazimiera',
  'Edyta',
  'Stefania',
  'Jan',
  'Andrzej',
  'Piotr',
  'Krzysztof',
  'Stanisław',
  'Tomasz',
  'Paweł',
  'Józef',
  'Marcin',
  'Marek',
  'Michał',
  'Grzegorz',
  'Jerzy',
  'Tadeusz',
  'Adam',
  'Łukasz',
  'Zbigniew',
  'Ryszard',
  'Dariusz',
  'Henryk',
  'Mariusz',
  'Kazimierz',
  'Wojciech',
  'Robert',
  'Mateusz',
  'Marian',
  'Rafał',
  'Jacek',
  'Janusz',
  'Mirosław',
  'Maciej',
  'Sławomir',
  'Jarosław',
  'Kamil',
  'Wiesław',
  'Roman',
  'Władysław',
  'Jakub',
  'Artur',
  'Zdzisław',
  'Edward',
  'Mieczysław',
  'Damian',
  'Dawid',
  'Przemysław',
  'Sebastian',
  'Czesław',
  'Leszek',
  'Daniel',
  'Waldemar',
  'Abigail',
  'Alexandra',
  'Alison',
  'Amanda',
  'Amelia',
  'Amy',
  'Andrea',
  'Angela',
  'Anna',
  'Anne',
  'Audrey',
  'Ava',
  'Bella',
  'Bernadette',
  'Carol',
  'Caroline',
  'Carolyn',
  'Chloe',
  'Claire',
  'Deirdre',
  'Diana',
  'Diane',
  'Donna',
  'Dorothy',
  'Elizabeth',
  'Ella',
  'Emily',
  'Emma',
  'Faith',
  'Felicity',
  'Fiona',
  'Gabrielle',
  'Grace',
  'Hannah',
  'Heather',
  'Irene',
  'Jan',
  'Jane',
  'Jasmine',
  'Jennifer',
  'Jessica',
  'Joan',
  'Joanne',
  'Julia',
  'Karen',
  'Katherine',
  'Kimberly',
  'Kylie',
  'Lauren',
  'Leah',
  'Lillian',
  'Lily',
  'Lisa',
  'Madeleine',
  'Maria',
  'Mary',
  'Megan',
  'Melanie',
  'Michelle',
  'Molly',
  'Natalie',
  'Nicola',
  'Olivia',
  'Penelope',
  'Pippa',
  'Rachel',
  'Rebecca',
  'Rose',
  'Ruth',
  'Sally',
  'Samantha',
  'Sarah',
  'Sonia',
  'Sophie',
  'Stephanie',
  'Sue',
  'Theresa',
  'Tracey',
  'Una',
  'Vanessa',
  'Victoria',
  'Virginia',
  'Wanda',
  'Wendy',
  'Yvonne',
  'Zoe',
  'Adam',
  'Adrian',
  'Alan',
  'Alexander',
  'Andrew',
  'Anthony',
  'Austin',
  'Benjamin',
  'Blake',
  'Boris',
  'Brandon',
  'Brian',
  'Cameron',
  'Carl',
  'Charles',
  'Christian',
  'Christopher',
  'Colin',
  'Connor',
  'Dan',
  'David',
  'Dominic',
  'Dylan',
  'Edward',
  'Eric',
  'Evan',
  'Frank',
  'Gavin',
  'Gordon',
  'Harry',
  'Ian',
  'Isaac',
  'Jack',
  'Jacob',
  'Jake',
  'James',
  'Jason',
  'Joe',
  'John',
  'Jonathan',
  'Joseph',
  'Joshua',
  'Julian',
  'Justin',
  'Keith',
  'Kevin',
  'Leonard',
  'Liam',
  'Lucas',
  'Luke',
  'Matt',
  'Max',
  'Michael',
  'Nathan',
  'Neil',
  'Nicholas',
  'Oliver',
  'Owen',
  'Paul',
  'Peter',
  'Phil',
  'Piers',
  'Richard',
  'Robert',
  'Ryan',
  'Sam',
  'Sean',
  'Sebastian',
  'Simon',
  'Stephen',
  'Steven',
  'Stewart',
  'Thomas',
  'Tim',
  'Trevor',
  'Victor',
  'Warren',
  'William'
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
  'Rzęsa',
  'Nowak',
  'Kowalski',
  'Wiśniewski',
  'Dąbrowski',
  'Lewandowski',
  'Wójcik',
  'Kamiński',
  'Kowalczyk',
  'Zieliński',
  'Szymański',
  'Woźniak',
  'Kozłowski',
  'Jankowski',
  'Wojciechowski',
  'Kwiatkowski',
  'Kaczmarek',
  'Mazur',
  'Krawczyk',
  'Piotrowski',
  'Grabowski',
  'Nowakowski',
  'Pawłowski',
  'Michalski',
  'Nowicki',
  'Adamczyk',
  'Dudek',
  'Zając',
  'Wieczorek',
  'Jabłoński',
  'Król',
  'Majewski',
  'Olszewski',
  'Jaworski',
  'Wróbel',
  'Malinowski',
  'Pawlak',
  'Witkowski',
  'Walczak',
  'Stępień',
  'Górski',
  'Rutkowski',
  'Michalak',
  'Sikora',
  'Ostrowski',
  'Baran',
  'Duda',
  'Szewczyk',
  'Tomaszewski',
  'Pietrzak',
  'Marciniak',
  'Wróblewski',
  'Zalewski',
  'Jakubowski',
  'Jasiński',
  'Zawadzki',
  'Sadowski',
  'Bąk',
  'Chmielewski',
  'Włodarczyk',
  'Borkowski',
  'Czarnecki',
  'Sawicki',
  'Sokołowski',
  'Urbański',
  'Kubiak',
  'Maciejewski',
  'Szczepański',
  'Kucharski',
  'Wilk',
  'Kalinowski',
  'Lis',
  'Mazurek',
  'Wysocki',
  'Adamski',
  'Kaźmierczak',
  'Wasilewski',
  'Sobczak',
  'Czerwiński',
  'Andrzejewski',
  'Cieślak',
  'Głowacki',
  'Zakrzewski',
  'Kołodziej',
  'Sikorski',
  'Krajewski',
  'Gajewski',
  'Szymczak',
  'Szulc',
  'Baranowski',
  'Laskowski',
  'Brzeziński',
  'Makowski',
  'Ziółkowski',
  'Przybylski',
  'Abraham',
  'Allan',
  'Alsop',
  'Anderson',
  'Arnold',
  'Avery',
  'Bailey',
  'Baker',
  'Ball',
  'Bell',
  'Berry',
  'Black',
  'Blake',
  'Bond',
  'Bower',
  'Brown',
  'Buckland',
  'Burgess',
  'Butler',
  'Cameron',
  'Campbell',
  'Carr',
  'Chapman',
  'Churchill',
  'Clark',
  'Clarkson',
  'Coleman',
  'Cornish',
  'Davidson',
  'Davies',
  'Dickens',
  'Dowd',
  'Duncan',
  'Dyer',
  'Edmunds',
  'Ellison',
  'Ferguson',
  'Fisher',
  'Forsyth',
  'Fraser',
  'Gibson',
  'Gill',
  'Glover',
  'Graham',
  'Grant',
  'Gray',
  'Greene',
  'Hamilton',
  'Hardacre',
  'Harris',
  'Hart',
  'Hemmings',
  'Henderson',
  'Hill',
  'Hodges',
  'Howard',
  'Hudson',
  'Hughes',
  'Hunter',
  'Ince',
  'Jackson',
  'James',
  'Johnston',
  'Jones',
  'Kelly',
  'Kerr',
  'King',
  'Knox',
  'Lambert',
  'Langdon',
  'Lawrence',
  'Lee',
  'Lewis',
  'Lyman',
  'MacDonald',
  'Mackay',
  'Mackenzie',
  'MacLeod',
  'Manning',
  'Marshall',
  'Martin',
  'Mathis',
  'May',
  'McDonald',
  'McLean',
  'McGrath',
  'Metcalfe',
  'Miller',
  'Mills',
  'Mitchell',
  'Morgan',
  'Morrison',
  'Murray',
  'Nash',
  'Newman',
  'Nolan',
  'North',
  'Ogden',
  'Oliver',
  'Paige',
  'Parr',
  'Parsons',
  'Paterson',
  'Payne',
  'Peake',
  'Peters',
  'Piper',
  'Poole',
  'Powell',
  'Pullman',
  'Quinn',
  'Rampling',
  'Randall',
  'Rees',
  'Reid',
  'Roberts',
  'Robertson',
  'Ross',
  'Russell',
  'Rutherford',
  'Sanderson',
  'Scott',
  'Sharp',
  'Short',
  'Simpson',
  'Skinner',
  'Slater',
  'Smith',
  'Springer',
  'Stewart',
  'Sutherland',
  'Taylor',
  'Terry',
  'Thomson',
  'Tucker',
  'Turner',
  'Underwood',
  'Vance',
  'Vaughan',
  'Walker',
  'Wallace',
  'Walsh',
  'Watson',
  'Welch',
  'White',
  'Wilkins',
  'Wilson',
  'Wright',
  'Young'
]

def grouper(iterable, n, fillvalue=None):
  args = [iter(iterable)] * n
  return zip_longest(*args, fillvalue=fillvalue)

def save_list(objDescription, objList, max_count_per_save=100):
  chunks_count = len(objList) // max_count_per_save
  chunks_i = 0
  for objChunk in grouper(objList, max_count_per_save, None):
    chunks_i = chunks_i + 1
    printProgress('Saving '+str(objDescription), chunks_i, chunks_count)
    with transaction.atomic():
      for obj in objChunk:
        if obj:
          obj.save()
  
def printProgress(task, current, maximum):

  global disableSockets

  if maximum <= 0:
    maximum = 1
  print('[DataGenerator] '+str(task)+' '+str(((current / maximum * 10000) // 10) / 10) + '%')
  if not disableSockets:
    try:
      channel_layer = get_channel_layer()
      async_to_sync(channel_layer.group_send)(
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
    except:
      disableSockets = True
      return False
    return True
  
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
           'message': 'Generated '+str(planes_count)+' plane/-s, '+str(flights_count)+' flight/-s and '+str(users_count)+' user/-s',
           'mode': 'progress_end'
        }
      )
    except:
      disableSockets = True
      return False
    return True
  
def generateFlight(plane, Flight, last_flight_status, plane_flights_count_per_day):
  global airports
  src = airports[randint(0, len(airports)-1)]
  dest = airports[randint(0, len(airports)-1)]
  while src == dest:
    dest = airports[randint(0, len(airports)-1)]
    
  if not last_flight_status:
    last_flight_status = {}
  if not 'end' in last_flight_status:
    last_flight_status['end'] = timezone.now()
  if not 'day_count' in last_flight_status:
    last_flight_status['day_count'] = 0
    
  minutes = randint(30, 60*3)
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
    'end': end,
    'day_count': day_count
  }
  
def generateUserData():
  surname = surnames[randint(0, len(surnames)-1)]
  name = names[randint(0, len(names)-1)]
  return {
    'surname': surname,
    'name': name,
    'flights': []
  }
  
def generateUser(user_data, User, user_names_table):
  user_name = user_data['surname'] + '|' + user_data['name']
  if user_name in user_names_table:
    return None
    
  user = User(surname=user_data['surname'], name=user_data['name'])
  #user.save()
  #user.flights.set(user_data['flights'])
  #user.save()
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
    userid = randint(0, len(user_samples)-1)
    tries = 0
    while userid in set_ids:
      userid = randint(0, len(user_samples)-1)
      tries = tries + 1
      if tries > 30:
        return user_samples
    set_ids[userid] = 'set'
    user_samples[userid]['flights'].append(flight)
  return user_samples

def PlanesGenerator(Plane, Flight, User, form_data):

  with transaction.atomic():
    User.objects.all().delete()
    Flight.objects.all().delete()
    Plane.objects.all().delete()
    
  input = form_data
  planes_data = []
  flights_data = []
  generated_planes = []
  generated_flights = []
    
  seats_samples = []
  seats_samples_count = 0
  user_samples = []
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
    
  #with transaction.atomic():
  
  print('Generate seats samples')
  
  seats_samples_count = randint(planes_count//4, planes_count//3) + 4
  for i in range(seats_samples_count):
    value = randint(plane_seats_count_min, plane_seats_count_max)
    valueMod = ( value // 10 ) * 10
    if valueMod >= plane_seats_count_min and valueMod <= plane_seats_count_max:
      value = valueMod
    seats_samples.append(value)
    
  print('Generate user samples')
    
  for i in range(users_count):
    user_samples.append(generateUserData())
  
  print('Generate times samples')
  
  times_samples_count = randint(planes_count//4, planes_count//3) + 4
  for i in range(times_samples_count):
    times_samples.append(randint(2, 2700))
  
  print('Start generating planes')
  
  for plane_index in range(planes_count):
    printProgress('Generating planes', plane_index+1, planes_count)
    
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
    generated_planes.append(plane)
    
    
  save_list('planes', generated_planes)

  for plane_index in range(planes_count):
    printProgress('Generating subscriptions', plane_index+1, planes_count)
    
    plane = generated_planes[plane_index]
    last_flight_status = {}
    subscription_count = randint(plane_flights_count_min, plane_flights_count_max)
    for flight_index in range(subscription_count):
      flight = generateFlight(plane, Flight, last_flight_status, plane_flights_count_per_day)
      flights_data.append(flight['flight'])
      last_flight_status = flight
      #flight['flight'].save()
      generated_flights.append(flight['flight'])
      user_samples = generateFlightSubscriptions(flight['flight'], user_samples)
    
  save_list('flights', generated_flights)
   
  print('Generate users')
  users_data = []
  users_objs = []
  user_names_table = {}
  for i in range(users_count):
    printProgress('Generating users', i+1, users_count)
    userGen = generateUser(user_samples[i], User, user_names_table)
    if userGen:
      users_objs.append(userGen['user_obj'])
      users_data.append(userGen['user_data'])
    
  save_list('users', users_objs)
  
  users_data_len = len(users_data)
  for i in range(users_data_len):
    printProgress('Matching users with flights', i+1, users_data_len)
    userInheritFlights(users_data[i])
    
  save_list('users with flights', users_objs)

  obj = {
    'planes': planes_data,
    'flights': flights_data,
    'users': users_data
  }
  
  printProgressEnd(obj)
  return obj