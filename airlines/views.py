from django.http import HttpResponse
from django.template import loader
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlencode
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlquote

from .models import Plane, Flight, User
from .forms import DataGeneratorForm, AddUserFlightForm
from .datagenerator.planes import PlanesGenerator

DEFAULT_PAGE_SIZE     = 30
FLIGHT_EDIT_PAGE_SIZE = 15

def paginateContent(pageName, request, data_list, attr_names, page_size=DEFAULT_PAGE_SIZE, link_has_params=False):
  
  global DEFAULT_PAGE_SIZE
  
  page = request.GET.get('page', 1)
  orderby = request.GET.get('orderby', '')
  mode = request.GET.get('mode', '')
  next_page = None
  previous_page = None
  first_page = None
  last_page = None
  
  orderby_attr_found = False
  for attr in attr_names:
    if orderby == attr:
      data_list = data_list.order_by(attr).reverse()
      orderby_attr_found = True
      break
  if not orderby_attr_found:
    orderby = attr_names[0]
  
  if mode == 'asc':
    data_list = data_list.reverse()
  elif mode == 'desc':
    mode = 'desc'
  else:
    data_list = data_list.reverse()
    mode = 'asc'
    
  paginator = Paginator(data_list, page_size)
  page_data = None
  
  def generatePageLink(pageno, newOrderBy=None, newMode=None):
    if not pageno:
      return None
    if not newMode:
      newMode = mode
    if not newOrderBy:
      newOrderBy = orderby
   
    if link_has_params:
      return pageName+'&page='+str(pageno)+'&orderby='+newOrderBy+'&mode='+newMode
    return pageName+'?page='+str(pageno)+'&orderby='+newOrderBy+'&mode='+newMode
  
  sort_links = {}
  for attr in attr_names:
    sort_links[attr] = {
      'link': generatePageLink(page, attr, 'desc'),
      'mode': ''
    }
  
  if orderby in sort_links:
    sort_links[orderby]['mode'] = 'sort-'+mode
    if mode == 'desc':
      sort_links[orderby]['link'] = generatePageLink(page, orderby, 'asc')

  try:
    page_data = paginator.page(page)
    page = int(page)
    if page < paginator.num_pages:
      next_page = page + 1
    if page > 1:
      previous_page = page - 1
  except PageNotAnInteger:
    page_data = paginator.page(1)
    page = 1
    next_page = 2
  except EmptyPage:
    page_data = paginator.page(paginator.num_pages)
    page = paginator.num_pages
    previous_page = page - 1

  if page != 1:
    first_page = 1
  if page != paginator.num_pages:
    last_page = paginator.num_pages
    
  pages = [
    {
      'link': generatePageLink(pageno),
      'no': pageno
    } for pageno in paginator.page_range
  ]
    
  pages_range = 5
  pages_min = page-pages_range
  if pages_min < 0:
    pages_min = 0
  
  pages_max = page+pages_range
  if pages_max > paginator.num_pages:
    pages_max = paginator.num_pages
    
  pages = pages[pages_min:pages_max]
    
  if len(pages) <= 1:
    pages = None
    
  return {
    'current_page': page,
    'pages': pages,
    'next_page': generatePageLink(next_page),
    'previous_page': generatePageLink(previous_page),
    'first_page': generatePageLink(first_page),
    'last_page': generatePageLink(last_page),
    'sort_links': sort_links,
    'page_data': page_data
  }
   
def renderContentPage(pageName, request, data_list, attr_list):
  context = paginateContent(pageName, request, data_list, attr_list)
  template = loader.get_template('index.html')
  context.update({
    'content': pageName
  })
  return HttpResponse(template.render(context, request))
   
def flights(request):
  data_list = Flight.objects.annotate(number_of_tickets=Count('tickets'))
  return renderContentPage(
    'flights',
    request,
    data_list,
    [
      'plane__reg_id', 'src', 'dest',
      'start', 'end', 'plane__seats_count',
      'number_of_tickets'
    ]
  )
  
def flightEdit(request):

  global FLIGHT_EDIT_PAGE_SIZE

  backURL = request.GET.get('back', None)
  id = request.GET.get('id', None)
  
  if not id:
    template = loader.get_template('index.html')
    context = {
      'content': 'flight-edit-not-found',
      'back_button': backURL
    }
    return HttpResponse(template.render(context, request))
  
  flight = Flight.objects.get(id=id)
  if not flight:
    template = loader.get_template('index.html')
    context = {
      'content': 'flight-edit-not-found',
      'back_button': backURL
    }
    return HttpResponse(template.render(context, request))
    
  template = loader.get_template('index.html')
 
  urlParams = urlencode({
    'back': backURL,
    'id': id
  })
  currentURL = 'flight-edit?' + urlParams
 
  flight_tickets = flight.tickets.all()
  context = paginateContent(currentURL, request, flight.tickets.all(), [
    'surname',
    'name'
  ], page_size=FLIGHT_EDIT_PAGE_SIZE, link_has_params=True)
  
  context.update({
    'content': 'flight-edit',
    'flight': flight,
    'back_button': backURL,
    'add_user_button': 'flight-add-user-flight?' + urlencode({
      'flightid': str(id),
      'back': urlParams
    }),
    'flight_fullness': ((flight_tickets.count() / flight.plane.seats_count * 10000) // 100)
  })
  
  page_data = context['page_data']
  context['page_data'] = [
    {
      'action_cancel': 'flight-cancel-user-flight?' + urlencode({
        'flightid': str(id),
        'userid': str(user.id),
        'back': urlParams
      }),
      'data': user
    } for user in page_data
  ]
  
  return HttpResponse(template.render(context, request))
  
def cancelUserFlight(request):
  flightid = request.GET.get('flightid', None)
  userid = request.GET.get('userid', None)
  backURL = request.GET.get('back', '')
  
  flight = Flight.objects.get(id=flightid)
  user = User.objects.get(id=userid) 
  flight.tickets.remove(user)
  flight.save()
  
  template = loader.get_template('index.html')
  context = {}
  messageOtps = 'info=' + urlquote('The flight of user '+user.name+' '+user.surname+' was cancelled.')
  return redirect(reverse('flightEdit') + '?' + messageOtps + '&' + backURL)

def addUserFlight(request):

  backURL = request.GET.get('back', '')
  flightid = request.GET.get('flightid', None)
  messageOtps = ''
  
  template = loader.get_template('index.html')
  context = {
    'content': 'add-user-form',
    'form': None
  }
  
  formActionURL = 'flight-add-user-flight?' + urlencode({
    'back': backURL,
    'flightid': flightid
  })
  
  def formDefaultRedirect():
    return redirect(reverse('flightEdit') + '?' + messageOtps + '&' + backURL)
  
  if request.method == 'POST':
    form = AddUserFlightForm(request.POST)
    if form.is_valid():
      context['content'] = 'add-user-form'
      form_data = form.cleaned_data
      
      user_name = form_data['user_name']
      user_surname = form_data['user_surname']
      
      try:
        flight = Flight.objects.get(id=flightid)
      except ObjectDoesNotExist:
        messageOtps = 'error=' + urlquote('The flight of given ID could not be found!')
        return formDefaultRedirect()
      
      if flight.tickets.count() >= flight.plane.seats_count:
        messageOtps = 'error=' + urlquote('The flight is full. Could not add new passanger.')
        return formDefaultRedirect()
      
      user = None
      try:
        user = User.objects.get(name=user_name, surname=user_surname)
        messageOtps = 'info=' + urlquote('The existing user was added to the flight.')
      except ObjectDoesNotExist:
        user = User(name=user_name, surname=user_surname)
        user.save()
        messageOtps = 'info=' + urlquote('New user was added to the flight.')
      
      flight.tickets.add(user)
      flight.save()
      
      return formDefaultRedirect()
      
  else:
    form = AddUserFlightForm()
   
  context['form'] = form
  context['formActionURL'] = formActionURL
  return HttpResponse(template.render(context, request))

  
def planes(request):
  data_list = Plane.objects.annotate(number_of_flights=Count('flight'))
  return renderContentPage(
    'planes',
    request,
    data_list,
    [
      'reg_id', 'seats_count',
      'service_start'
    ]
  )
  
  
def users(request):
  data_list = User.objects.annotate(number_of_flights=Count('flights'))
  return renderContentPage(
    'users',
    request,
    data_list,
    [
      'name', 'surname', 'number_of_flights'
    ]
  )
  
def dataGenerator(request):
  template = loader.get_template('data-generator.html')
  context = {
    'content': 'data-generator',
    'form': None
  }
  
  if request.method == 'POST':
    form = DataGeneratorForm(request.POST)
    if form.is_valid():
      context['content'] = 'data-generator-answer'
      data = PlanesGenerator(Plane, Flight, User, form)
      context['content_message'] = 'Generated '+str(len(data['planes']))+' planes and '+str(len(data['flights']))+' flights'
      
  else:
    #form = DataGeneratorForm(initial={
    #  'users_count': 5,
    #  'planes_count': 1,
    #  'plane_seats_count_min': 1,
    #  'plane_seats_count_max': 2,
    #  'plane_flights_count_min': 2,
    #  'plane_flights_count_max': 4,
    #  'plane_reg_format': 'CCCNNNNNN'
    #})
    form = DataGeneratorForm(initial={
      'users_count': 1000,
      'planes_count': 60,
      'plane_seats_count_min': 11,
      'plane_seats_count_max': 450,
      'plane_flights_count_min': 0,
      'plane_flights_count_max': 18,
      'plane_reg_format': 'CCCNNNNNN'
    })
   
  context['form'] = form
   
  return HttpResponse(template.render(context, request))
    
  #template = loader.get_template('data-generator.html')
  #context = {
  #  'content': 'data-generator'
  #}
  #return HttpResponse(template.render(context, request))
  
  
def dataGeneratorPopup(request):
  template = loader.get_template('popups/data-generator.html')
  context = {
    'content': 'data-generator'
  }
  return HttpResponse(template.render(context, request))
  
def adminPopup(request):
  template = loader.get_template('popups/admin.html')
  context = {
    'content': 'admin'
  }
  return HttpResponse(template.render(context, request))
  
def index(request):
  return flights(request)