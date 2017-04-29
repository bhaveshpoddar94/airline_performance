from __future__ import unicode_literals
from django.db import models

# Create your models here.
class Airline(models.Model):
    air_id = models.IntegerField(primary_key=True)
    carrier_code = models.CharField(max_length=30)

class Airport(models.Model):
	port_id = models.IntegerField(primary_key=True)
	port_code = models.CharField(max_length=10)
	state_code = models.CharField(max_length=10)
	city_name = models.CharField(max_length=30)
	state_name = models.CharField(max_length=30)

class AirlineFlight(models.Model):
	airline = models.ForeignKey(Airline)
	flight_no = models.IntegerField()

class Performance(models.Model):
	crs_time = models.DateTimeField()
	actual_time = models.DateTimeField()
	delay = models.IntegerField()
	is_delay = models.BooleanField(default=False)

class Trip(models.Model):
	air_flight = models.ForeignKey(AirlineFlight)
	origin = models.ForeignKey(Airport, related_name='origin')
	destination = models.ForeignKey(Airport, related_name='destination')
	month = models.PositiveIntegerField()
	week = models.PositiveIntegerField()
	distance = models.PositiveIntegerField()
	tail_num = models.CharField(max_length=30)
	is_cancelled = models.BooleanField(default=False)
	cancel_code = models.CharField(max_length=10)
	is_diverted = models.BooleanField(default=False)
	crs_elapsed_time = models.PositiveIntegerField()
	actual_elapsed_time = models.PositiveIntegerField()
	arr_perf = models.ForeignKey(Performance, related_name='arrival')
	dep_perf = models.ForeignKey(Performance, related_name='departure')


class Delayed(models.Model):
	carrier = models.PositiveIntegerField()
	weather = models.PositiveIntegerField()
	nas = models.PositiveIntegerField()
	security = models.PositiveIntegerField()
	late_aircraft = models.PositiveIntegerField()
	trip = models.ForeignKey(Trip)




