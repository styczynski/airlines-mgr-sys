from django.db import models

class Plane(models.Model):
  reg_id = models.CharField('Registration identificator', max_length=200, unique=True)
  seats_count = models.IntegerField('Seats')
  service_start = models.DateTimeField('In service since')
  def __str__(self):
    return 'Plane '+self.reg_id
    
class User(models.Model):
  surname = models.CharField('Surname', max_length=100)
  name = models.CharField('Name', max_length=100)
  flights = models.ManyToManyField('Flight', blank=True)
  
  class Meta:
    unique_together = ('surname', 'name',)
  
  def __str__(self):
    return 'User '+self.surname+' '+self.name

class Crew(models.Model):
  crew_id = models.CharField('Crew ID', max_length=15)
  
  def __str__(self):
    return 'Crew'
    
class Flight(models.Model):
  src = models.CharField('Source airport', max_length=200)
  dest = models.CharField('Destination airport', max_length=200)
  start = models.DateTimeField('Start date')
  end = models.DateTimeField('Landing date')
  plane = models.ForeignKey(Plane, on_delete=models.PROTECT, null=True)
  tickets = models.ManyToManyField('User', through=User.flights.through, blank=True)
  crew = models.ForeignKey(Crew, on_delete=models.CASCADE, null=True)
  
  def __str__(self):
    return 'Flight '+self.src+' -> '+self.dest
    
class Worker(models.Model):
  surname = models.CharField('Surname', max_length=100)
  name = models.CharField('Name', max_length=100)
  crew = models.ForeignKey(Crew, on_delete=models.CASCADE, null=True)
  
  class Meta:
    unique_together = ('surname', 'name',)
  
  def __str__(self):
    return 'Worker '+self.surname+' '+self.name
    