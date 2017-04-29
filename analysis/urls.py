from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'login/', views.login, name = 'login'),
    url(r'register/', views.register, name = 'register'),
    url(r'ba-home/', views.ba_home, name = 'ba_home'),
    url(r'api/busiest-airports/', views.busiest_airports, name='bairports'),
    url(r'br-home/', views.br_home, name = 'br_home'),
    url(r'api/busiest-routes/', views.busiest_routes, name='broutes'),
    url(r'performance/', views.perf_home, name = 'perf_home'),
    url(r'api/perf/', views.performance, name='performance'),
    url(r'delayed-flights/', views.delayed_flights, name='delayed_flights'),
    url(r'api/flight-desc/', views.flight_desc, name='flight_desc'),
    url(r'delayed-percent/', views.delayed_percent, name='delayed_percent'),
    url(r'aprof-home/', views.aprof_home, name='aprof_home'),
    url(r'airline-profile/', views.airline_profile, name='airline_profile')
]