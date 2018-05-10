from .models import Plane, Flight, User
from django import forms

class DataGeneratorForm(forms.Form):
  users_count = forms.DecimalField(label='No. of users to be generated', min_value=1, max_value=1000000)
  planes_count = forms.DecimalField(label='No. of planes to be generated', min_value=1, max_value=1000000)
  plane_seats_count_min = forms.DecimalField(label='Minimum number of seats', min_value=0, max_value=10000)
  plane_seats_count_max = forms.DecimalField(label='Maximum number of seats', min_value=0, max_value=10000)
  plane_flights_count_min = forms.DecimalField(label='Minimum number of flights per plane', min_value=0, max_value=10000)
  plane_flights_count_max = forms.DecimalField(label='Maximum number of flights per plane', min_value=0, max_value=10000)
  plane_reg_format = forms.ChoiceField(label='Plane reg. format', choices=[
    ('CCCNNNNNN', '3-letter 6-digit registration'),
    ('........', '8-character hash'),
  ])

class AddUserFlightForm(forms.Form):
  user_name =forms.CharField(label='User surname')
  user_surname =forms.CharField(label='User name')

class FilterFlightsForm(forms.Form):
  from_date = forms.DateField(widget=forms.SelectDateWidget())
  to_date = forms.DateField(widget=forms.SelectDateWidget())
