#
# Django views for airlines management sysyem
# MIT Piotr Styczyński 2018
#
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

from .models import Plane, Flight, User, Crew, Worker
from .forms import DataGeneratorForm, AddUserFlightForm, FilterFlightsForm
from .datagenerator.planes import PlanesGenerator

from . import rendering

#
# Maximum number of rows per single flight edit page
#
FLIGHT_EDIT_PAGE_SIZE = 15


#
# Default page with flights list
#
def flights(request):
    filter_date_from = request.GET.get('date-from', None)
    filter_date_to = request.GET.get('date-to', None)

    formActionURL = rendering.argurl(
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

            filtered_url = rendering.argurl(
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
                    'crew_id': (flight.crew.crew_id if flight.crew else None),
                    'seats_count': flight.plane.seats_count,
                    'tickets_count': flight.tickets.count,
                    'plane_reg_id': flight.plane.reg_id,
                    'flight_link': rendering.argurl(
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
        data_list = data_list.filter(start__date__gte=filter_date_from)

    if filter_date_to:
        data_list = data_list.filter(end__date__lte=filter_date_to)

    return rendering.renderContentPage(
        'flights',
        request,
        data_list,
        [
            'plane__reg_id', 'src', 'dest',
            'start', 'end', 'plane__seats_count',
            'number_of_tickets',
            'crew_id'
        ],
        mapping=mapFlightData
    )


#
# Flight editor page
#
def flightEdit(request):
    global FLIGHT_EDIT_PAGE_SIZE

    backURL = rendering.getBackURL(request)
    id = request.GET.get('id', None)

    if not id:
        template = loader.get_template('index.html')
        context = {
            'content': 'flight-edit-not-found',
            'back_button': backURL
        }
        return rendering.renderContentTemplate(request, context, template)

    flight = Flight.objects.get(id=id)
    if not flight:
        template = loader.get_template('index.html')
        context = {
            'content': 'flight-edit-not-found',
            'back_button': backURL
        }
        return rendering.renderContentTemplate(request, context, template)

    template = loader.get_template('index.html')

    flight_tickets = flight.tickets.all()
    context = rendering.paginateContent('flight-edit', {
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
        'add_user_button': rendering.argurl('addUserFlight', {
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
            'action_cancel': rendering.argurl('cancelUserFlight', {
                'flightid': str(id),
                'userid': str(user.id)
            }, currentPageRequest=request),
            'data': user
        } for user in page_data
    ]

    return rendering.renderContentTemplate(request, context, template)


#
# Temporary view for canelling users flights in the flight editor
#
@login_required
def cancelUserFlight(request):
    flightid = request.GET.get('flightid', None)
    userid = request.GET.get('userid', None)
    backURL = rendering.getBackURL(request, proxyBack=True)

    flight = Flight.objects.get(id=flightid)
    user = User.objects.get(id=userid)
    flight.tickets.remove(user)
    flight.save()

    template = loader.get_template('index.html')
    context = {}
    backURL = rendering.getBackURL(request, {
        'info': urlquote('The flight of user ' + user.name + ' ' + user.surname + ' was cancelled.')
    }, proxyBack=True)
    return redirect(backURL)


#
# Temporary view for adding new users to flight in the flight editor
#
@login_required
def addUserFlight(request):
    backURL = rendering.getBackURL(request, proxyBack=True)
    flightid = request.GET.get('flightid', None)
    messageOtps = ''

    template = loader.get_template('index.html')
    context = {
        'content': 'add-user-form',
        'form': None
    }

    formActionURL = rendering.argurl(
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
                backURL = rendering.getBackURL(request, {
                    'error': urlquote('The flight of given ID could not be found!')
                }, proxyBack=True)
                return formDefaultRedirect()

            if flight.tickets.count() >= flight.plane.seats_count:
                backURL = rendering.getBackURL(request, {
                    'error': urlquote('The flight is full. Could not add new passanger.')
                }, proxyBack=True)
                return formDefaultRedirect()

            user = None
            try:
                user = User.objects.get(name=user_name, surname=user_surname)
                backURL = rendering.getBackURL(request, {
                    'info': urlquote('The existing user was added to the flight.')
                }, proxyBack=True)
            except ObjectDoesNotExist:
                user = User(name=user_name, surname=user_surname)
                user.save()
                backURL = rendering.getBackURL(request, {
                    'info': urlquote('New user was added to the flight.')
                }, proxyBack=True)

            flight.tickets.add(user)
            flight.save()

            return formDefaultRedirect()

    else:
        form = AddUserFlightForm()

    context['form'] = form
    context['formActionURL'] = formActionURL

    return rendering.renderContentTemplate(request, context, template)

#
# List of all available planes
#
def planes(request):
    data_list = Plane.objects.annotate(number_of_flights=Count('flight'))
    return rendering.renderContentPage(
        'planes',
        request,
        data_list,
        [
            'reg_id', 'seats_count',
            'service_start'
        ]
    )

#
# List of all registered users
#
def users(request):
    data_list = User.objects.annotate(number_of_flights=Count('flights'))
    return rendering.renderContentPage(
        'users',
        request,
        data_list,
        [
            'name', 'surname', 'number_of_flights'
        ]
    )

#
# List of all registered crews
#
def crews(request):
    data_list = Crew.objects.annotate(number_of_workers=Count('worker'))
    return rendering.renderContentPage(
        'crews',
        request,
        data_list,
        [
            'crew_id', 'number_of_workers'
        ]
    )


#
# List of all registered workers
#
def workers(request):
    data_list = Worker.objects.all()
    return rendering.renderContentPage(
        'workers',
        request,
        data_list,
        [
            'name', 'surname', 'crew__crew_id'
        ]
    )

#
# Returns static page for crews assignments
#
def crewsPanel(request):
    return rendering.renderStaticPage('crews-panel')

#
# Task for generating example database using the data generator
#
@background(schedule=0)
def dataGeneratorTask(form):
    context = {}
    data = PlanesGenerator(Plane, Flight, User, Worker, Crew, form)
    context['content_message'] = 'Generated ' + str(len(data['planes'])) + ' plane/-s, ' + str(
        len(data['flights'])) + ' flight/-s and ' + str(len(data['users'])) + ' user/-s'
    context['content'] = 'data-generator-answer'


#
# Data generator input form
#
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
                'workers_count': int(input['workers_count']),
                'planes_count': int(input['planes_count']),
                'plane_seats_count_min': int(input['plane_seats_count_min']),
                'plane_seats_count_max': int(input['plane_seats_count_max']),
                'plane_flights_count_min': int(input['plane_flights_count_min']),
                'plane_flights_count_max': int(input['plane_flights_count_max']),
                'plane_flights_count_per_day': int(input['plane_flights_count_per_day']),
                'plane_reg_format': str(input['plane_reg_format']),
            })

    else:
        if True:  # For debug purposes
            form = DataGeneratorForm(initial={
                'users_count': 1000,
                'workers_count': 500,
                'planes_count': 50,
                'plane_seats_count_min': 20,
                'plane_seats_count_max': 500,
                'plane_flights_count_min': 50,
                'plane_flights_count_max': 60,
                'plane_flights_count_per_day': 4,
                'plane_reg_format': 'CCCNNNNNN'
            })
        else:
            form = DataGeneratorForm(initial={
                'users_count': 3500,
                'workers_count': 930,
                'planes_count': 91,
                'plane_seats_count_min': 20,
                'plane_seats_count_max': 500,
                'plane_flights_count_min': 50,
                'plane_flights_count_max': 75,
                'plane_flights_count_per_day': 4,
                'plane_reg_format': 'CCC-NNNNNN'
            })

    context['form'] = form

    return rendering.renderContentTemplate(request, context, template)

    # template = loader.get_template('data-generator.html')
    # context = {
    #  'content': 'data-generator'
    # }
    # return HttpResponse(template.render(context, request))


#
# Popup containing data generator form
#
@login_required
def dataGeneratorPopup(request):
    template = loader.get_template('popups/data-generator.html')
    context = {
        'content': 'data-generator'
    }
    return rendering.renderContentTemplate(request, context, template)

#
# Popup containing Django administration panel
#
@login_required
def adminPopup(request):
    template = loader.get_template('popups/admin.html')
    context = {
        'content': 'admin'
    }
    return rendering.renderContentTemplate(request, context, template)

#
# View containg server status
#
@login_required
def serverStatus(request):
    template = loader.get_template('index.html')
    context = {
        'content': 'server-status'
    }
    return rendering.renderContentTemplate(request, context, template)

#
# Main application page
#
def index(request):
    template = loader.get_template('index.html')
    context = {
        'content': 'home'
    }
    return rendering.renderContentTemplate(request, context, template)
