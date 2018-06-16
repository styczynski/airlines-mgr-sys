#
# Django forms for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from .models import Plane, Flight, User
from django import forms

#
# Form that is submitted to the data generator to generate data samples in the database.
#
class DataGeneratorForm(forms.Form):
    #users_count = forms.DecimalField(label='No. of users to be generated', min_value=500, max_value=1000000)
    #workers_count = forms.DecimalField(label='No. of workers to be generated', min_value=500, max_value=10000)
    #planes_count = forms.DecimalField(label='No. of planes to be generated', min_value=50, max_value=1000000)
    #plane_seats_count_min = forms.DecimalField(label='Minimum number of seats', min_value=20, max_value=10000)
    #plane_seats_count_max = forms.DecimalField(label='Maximum number of seats', min_value=20, max_value=10000)
    #plane_flights_count_min = forms.DecimalField(label='Minimum number of flights per plane', min_value=50,
    #                                             max_value=10000)
    #plane_flights_count_max = forms.DecimalField(label='Maximum number of flights per plane', min_value=50,
    #                                             max_value=10000)
    #plane_flights_count_per_day = forms.DecimalField(label='Maximum number of plane\'s flights per day', min_value=4,
    #                                                 max_value=10000)
    #plane_reg_format = forms.ChoiceField(label='Plane reg. format', choices=[
    #    ('CCCNNNNNN', '3-letter 6-digit registration'),
    #    ('........', '8-character hash'),
    #])
    users_count = forms.DecimalField(label='No. of users to be generated', min_value=0, max_value=1000000)
    workers_count = forms.DecimalField(label='No. of workers to be generated', min_value=0, max_value=10000)
    planes_count = forms.DecimalField(label='No. of planes to be generated', min_value=0, max_value=1000000)
    plane_seats_count_min = forms.DecimalField(label='Minimum number of seats', min_value=0, max_value=10000)
    plane_seats_count_max = forms.DecimalField(label='Maximum number of seats', min_value=0, max_value=10000)
    plane_flights_count_min = forms.DecimalField(label='Minimum number of flights per plane', min_value=0,
                                                 max_value=10000)
    plane_flights_count_max = forms.DecimalField(label='Maximum number of flights per plane', min_value=0,
                                                 max_value=10000)
    plane_flights_count_per_day = forms.DecimalField(label='Maximum number of plane\'s flights per day', min_value=0,
                                                     max_value=10000)
    plane_reg_format = forms.ChoiceField(label='Plane reg. format', choices=[
        ('CCCNNNNNN', '3-letter 6-digit registration'),
        ('........', '8-character hash'),
    ])


#
# For for adding users to the existing flight
#
class AddUserFlightForm(forms.Form):
    user_name = forms.CharField(label='User surname')
    user_surname = forms.CharField(label='User name')


#
# Form to filter out the flights by specified details
#
class FilterFlightsForm(forms.Form):
    from_date = forms.DateField(required=False, widget=forms.SelectDateWidget())
    to_date = forms.DateField(required=False, widget=forms.SelectDateWidget())
