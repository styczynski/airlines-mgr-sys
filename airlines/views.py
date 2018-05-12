from django.http import HttpResponse
from django.template import loader
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlencode
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError
from django.urls import NoReverseMatch
from django.utils.http import urlquote, urlunquote
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from background_task import background
import json

from .models import Plane, Flight, User
from .forms import DataGeneratorForm, AddUserFlightForm, FilterFlightsForm
from .datagenerator.planes import PlanesGenerator

DEFAULT_PAGE_SIZE     = 30
FLIGHT_EDIT_PAGE_SIZE = 15

def argurl(pageName, pageAttrs={}, fullUri=False, uriScheme=None, currentPageName=None, currentPageParams=None, currentPageRequest=None, doNotGenerateBack=False, proxyBack=False, backParams=None, passAttrs=False, passExcept=None):
    if not currentPageParams:
        if currentPageRequest:
            currentPageParams =  currentPageRequest.GET.dict()
    if not currentPageName:
        if currentPageRequest:
            currentPageName = currentPageRequest.resolver_match.view_name
    if not pageName:
        pageName = currentPageName

    reverseURL = '/'
    try:
      reverseURL = reverse(pageName)
      if fullUri:
        if currentPageRequest:
          scheme = currentPageRequest.scheme
          if uriScheme:
            scheme = uriScheme
          reverseURL =  "{0}://{1}{2}".format(scheme, currentPageRequest.get_host(), reverseURL)
    except NoReverseMatch:
        reverseURL = pageName

    if not currentPageParams:
        currentPageParams = {}

    currentPageParamsDup = {
        **currentPageParams
    }

    previousBackParams = currentPageParams.get('back-params', '')
    previousBack = currentPageParams.get('back', '')

    currentPageParamsDup.pop('back-params', None)
    currentPageParamsDup.pop('back', None)

    if passAttrs:
        if not passExcept:
          pageAttrs = {
              **currentPageParams,
              **pageAttrs
          }
        else:
          pageAttrsNew = {}
          for k, v in currentPageParams.items():
            if k not in passExcept:
              pageAttrsNew[k] = v
          pageAttrs = {
            **pageAttrsNew,
            **pageAttrs
          }
          

    currentPageParams = currentPageParamsDup

    backs = {
        # TODO: Switch this to quote bacouse it should be then unquoted :(
        'back-params': urlquote(json.dumps(currentPageParams)),
        'back': currentPageName
    }

    if not proxyBack:
        if doNotGenerateBack:
            backs = {}

    if not reverseURL.endswith('?'):
        reverseURL = reverseURL + '?'

    if proxyBack:
        backs = {
            'back-params': previousBackParams,
            'back': previousBack
        }

    if backParams:
        if not (reverseURL.endswith('?') or reverseURL.endswith('&')):
            reverseURL = reverseURL + '&'
        reverseURL = reverseURL + backParams
        if not (reverseURL.endswith('?') or reverseURL.endswith('&')):
            reverseURL = reverseURL + '&'

    return reverseURL + urlencode({
        **pageAttrs,
        **backs
    })

def getBackURL(request, params={}, proxyBack=False):
    backURL = request.GET.get('back', None)
    backParams = request.GET.get('back-params', None)
    if backParams:
        backParams = json.loads(urlunquote(backParams))
    else:
        backParams = {}

    if proxyBack:
        return argurl(
            backURL,
            {
                **backParams,
                **params
            },
            proxyBack=True,
            currentPageRequest=request
        )
    return argurl(
        backURL,
        {
            **backParams,
            **params
        },
        doNotGenerateBack=True,
        currentPageRequest=request
    )


def useServerStatus(request, context):
  context.update({
    'server_status_url': argurl(
      'serverStatus',
      doNotGenerateBack=True,
      currentPageRequest=request,
      fullUri=True,
      uriScheme='ws'
    )
    
    #request.build_absolute_uri() + '/server_status' #'ws://localhost:8000/airlines/server_status'
  })

    
def paginateContent(pageName, pageAttrs, request, data_list, attr_names, page_size=DEFAULT_PAGE_SIZE):

  global DEFAULT_PAGE_SIZE

  force_empty_page_data = False
  
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

  def generatePageLink(pageno, newOrderBy=None, newMode=None, doNotGenerateBack=False):
    
    if not pageno:
      return None
    if not newMode:
      newMode = mode
    if not newOrderBy:
      newOrderBy = orderby

    #if link_has_params:
    #  return pageName+'&page='+str(pageno)+'&orderby='+newOrderBy+'&mode='+newMode
    #return pageName+'?page='+str(pageno)+'&orderby='+newOrderBy+'&mode='+newMode

    return argurl(
        None,
        {
            **pageAttrs,
            'page': str(pageno),
            'orderby': newOrderBy,
            'mode': newMode
        },
        currentPageRequest=request,
        doNotGenerateBack=doNotGenerateBack
    )

  sort_links = {}
  for attr in attr_names:
    sort_links[attr] = {
      'link': generatePageLink(page, attr, 'desc', doNotGenerateBack=True),
      'mode': ''
    }

  if orderby in sort_links:
    sort_links[orderby]['mode'] = 'sort-'+mode
    if mode == 'desc':
      sort_links[orderby]['link'] = generatePageLink(page, orderby, 'asc', doNotGenerateBack=True)

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
  except OperationalError:
    page_data = []
    force_empty_page_data = True
    
  
  if not force_empty_page_data:  
    if page != 1:
      first_page = 1
    if page != paginator.num_pages:
      last_page = paginator.num_pages

  if not force_empty_page_data:
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
  else:
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

def renderContentTemplate(request, context, template):
  try:
    useServerStatus(request, context)
    if request.user.is_authenticated:
      context.update({
        'user_auth': request.user
      })
    else:
      context.update({
        'user_auth': None
      })
  except OperationalError:
    context.update({
      'user_auth': None
    })
  return HttpResponse(template.render(context, request))
  
  
def renderContentPage(pageName, request, data_list, attr_list, mapping=None):
  context = paginateContent(pageName, {}, request, data_list, attr_list)
  template = loader.get_template('index.html')
  context.update({
    'content': pageName
  })
  try:
    if request.user.is_authenticated:
      context.update({
        'user_auth': request.user
      })
    else:
      context.update({
        'user_auth': None
      })
  except OperationalError:
    context.update({
      'user_auth': None
    })
    
  if mapping:
      context = mapping(context)
      
  useServerStatus(request, context)
  return renderContentTemplate(request, context, template)
  

def flights(request):

  filter_date_from = request.GET.get('date-from', None)
  filter_date_to = request.GET.get('date-to', None)


  formActionURL = argurl(
      None,
      {},
      currentPageRequest=request,
      passAttrs=True,
      passExcept=[
        'date-from',
        'date-to'
      ]
  )

  filter_form = None

  if request.method == 'POST':
    filter_form = FilterFlightsForm(request.POST)
    if filter_form.is_valid():
      form_data = filter_form.cleaned_data
      
      urlParams = {}
      if form_data['from_date']:
        urlParams['date-from'] = form_data['from_date']
      if form_data['to_date']:
        urlParams['date-to'] = form_data['to_date']
      
      filtered_url = argurl(
        None,
        urlParams,
        currentPageRequest=request,
        passAttrs=True
      )
      return redirect(filtered_url)
  else:
    filter_form = FilterFlightsForm(initial={
        'from_date': filter_date_from,
        'to_date': filter_date_to
    })

  def mapFlightData(context):
      if 'page_data' in context:
          page_data = []
          for flight in context['page_data']:
              page_data.append({
                **vars(flight),
                'seats_count': flight.plane.seats_count,
                'tickets_count': flight.tickets.count,
                'plane_reg_id': flight.plane.reg_id,
                'flight_link': argurl(
                    'flightEdit',
                    {
                      'id': str(flight.id)
                    },
                    currentPageRequest=request
                )
              })
          context['page_data'] = page_data
      context['filter_form'] = filter_form
      context['filter_action_url'] = formActionURL
      return context

  data_list = Flight.objects.annotate(number_of_tickets=Count('tickets'))

  if filter_date_from:
      data_list = data_list.filter(start__gte=filter_date_from)

  if filter_date_to:
      data_list = data_list.filter(end__lte=filter_date_to)

  return renderContentPage(
    'flights',
    request,
    data_list,
    [
      'plane__reg_id', 'src', 'dest',
      'start', 'end', 'plane__seats_count',
      'number_of_tickets'
    ],
    mapping=mapFlightData
  )

def flightEdit(request):

  global FLIGHT_EDIT_PAGE_SIZE

  backURL = getBackURL(request)
  id = request.GET.get('id', None)

  if not id:
    template = loader.get_template('index.html')
    context = {
      'content': 'flight-edit-not-found',
      'back_button': backURL
    }
    return renderContentTemplate(request, context, template)

  flight = Flight.objects.get(id=id)
  if not flight:
    template = loader.get_template('index.html')
    context = {
      'content': 'flight-edit-not-found',
      'back_button': backURL
    }
    return renderContentTemplate(request, context, template)

  template = loader.get_template('index.html')

  flight_tickets = flight.tickets.all()
  context = paginateContent('flight-edit', {
    'back': backURL,
    'id': id
  }, request, flight.tickets.all(), [
    'surname',
    'name'
  ], page_size=FLIGHT_EDIT_PAGE_SIZE)

  context.update({
    'content': 'flight-edit',
    'flight': flight,
    'back_button': backURL,
    'add_user_button': argurl('addUserFlight', {
      'flightid': str(id)
    }, currentPageRequest=request),
    'flight_fullness': ((flight_tickets.count() / flight.plane.seats_count * 10000) // 100)
  })
  
  if request.user.is_authenticated:
    context.update({
      'user_auth': request.user
    })
  else:
    context.update({
      'user_auth': None
    })
  
  page_data = context['page_data']
  context['page_data'] = [
    {
      'action_cancel': argurl('cancelUserFlight', {
        'flightid': str(id),
        'userid': str(user.id)
      }, currentPageRequest=request),
      'data': user
    } for user in page_data
  ]
  
  return renderContentTemplate(request, context, template)

@login_required
def cancelUserFlight(request):
  flightid = request.GET.get('flightid', None)
  userid = request.GET.get('userid', None)
  backURL = getBackURL(request, proxyBack=True)

  flight = Flight.objects.get(id=flightid)
  user = User.objects.get(id=userid)
  flight.tickets.remove(user)
  flight.save()

  template = loader.get_template('index.html')
  context = {}
  backURL = getBackURL(request, {
    'info': urlquote('The flight of user '+user.name+' '+user.surname+' was cancelled.')
  }, proxyBack=True)
  return redirect(backURL)

@login_required
def addUserFlight(request):

  backURL = getBackURL(request, proxyBack=True)
  flightid = request.GET.get('flightid', None)
  messageOtps = ''

  template = loader.get_template('index.html')
  context = {
    'content': 'add-user-form',
    'form': None
  }

  formActionURL = argurl(
      None,
      {
        'flightid': flightid
      },
      currentPageRequest=request,
      proxyBack=True
  )

  def formDefaultRedirect():
    return redirect(backURL)

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
        backURL = getBackURL(request, {
            'error': urlquote('The flight of given ID could not be found!')
        }, proxyBack=True)
        return formDefaultRedirect()

      if flight.tickets.count() >= flight.plane.seats_count:
        backURL = getBackURL(request, {
            'error': urlquote('The flight is full. Could not add new passanger.')
        }, proxyBack=True)
        return formDefaultRedirect()

      user = None
      try:
        user = User.objects.get(name=user_name, surname=user_surname)
        backURL = getBackURL(request, {
            'info': urlquote('The existing user was added to the flight.')
        }, proxyBack=True)
      except ObjectDoesNotExist:
        user = User(name=user_name, surname=user_surname)
        user.save()
        backURL = getBackURL(request, {
            'info': urlquote('New user was added to the flight.')
        }, proxyBack=True)

      flight.tickets.add(user)
      flight.save()

      return formDefaultRedirect()

  else:
    form = AddUserFlightForm()

  context['form'] = form
  context['formActionURL'] = formActionURL

  return renderContentTemplate(request, context, template)


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

@background(schedule=0)
def dataGeneratorTask(form):
  context = {}
  data = PlanesGenerator(Plane, Flight, User, form)
  context['content_message'] = 'Generated '+str(len(data['planes']))+' plane/-s, '+str(len(data['flights']))+' flight/-s and '+str(len(data['users']))+' user/-s'
  context['content'] = 'data-generator-answer'
  
  
@login_required
def dataGenerator(request, contextPrototype={}):
  template = loader.get_template('data-generator.html')
  context = {
    **contextPrototype,
    'content': 'data-generator',
    'form': None
  }

  if request.method == 'POST':
    form = DataGeneratorForm(request.POST)
    if form.is_valid():
      context['content'] = 'data-generator-answer'
      input = form.cleaned_data
      dataGeneratorTask({
        'users_count': int(input['users_count']),
        'planes_count': int(input['planes_count']),
        'plane_seats_count_min': int(input['plane_seats_count_min']),
        'plane_seats_count_max': int(input['plane_seats_count_max']),
        'plane_flights_count_min': int(input['plane_flights_count_min']),
        'plane_flights_count_max': int(input['plane_flights_count_max']),
        'plane_flights_count_per_day': int(input['plane_flights_count_per_day']),
        'plane_reg_format': str(input['plane_reg_format']),
      })

  else:
    if False: # For debug purposes
      form = DataGeneratorForm(initial={
        'users_count': 5,
        'planes_count': 1,
        'plane_seats_count_min': 1,
        'plane_seats_count_max': 2,
        'plane_flights_count_min': 2,
        'plane_flights_count_max': 4,
        'plane_flights_count_per_day': 5,
        'plane_reg_format': 'CCCNNNNNN'
      })
    else:
      form = DataGeneratorForm(initial={
        'users_count': 3500,
        'planes_count': 91,
        'plane_seats_count_min': 20,
        'plane_seats_count_max': 500,
        'plane_flights_count_min': 50,
        'plane_flights_count_max': 75,
        'plane_flights_count_per_day': 4,
        'plane_reg_format': 'CCC-NNNNNN'
      })

  context['form'] = form
  
  return renderContentTemplate(request, context, template)

  #template = loader.get_template('data-generator.html')
  #context = {
  #  'content': 'data-generator'
  #}
  #return HttpResponse(template.render(context, request))

@login_required
def dataGeneratorPopup(request):
  template = loader.get_template('popups/data-generator.html')
  context = {
    'content': 'data-generator'
  }
  return renderContentTemplate(request, context, template)

@login_required
def adminPopup(request):
  template = loader.get_template('popups/admin.html')
  context = {
    'content': 'admin'
  }
  return renderContentTemplate(request, context, template)

@login_required
def serverStatus(request):
  template = loader.get_template('index.html')
  context = {
    'content': 'server-status'
  }
  return renderContentTemplate(request, context, template)
  
def index(request):
  template = loader.get_template('index.html')
  context = {
    'content': 'home'
  }
  return renderContentTemplate(request, context, template)
