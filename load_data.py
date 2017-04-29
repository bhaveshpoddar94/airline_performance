import airline.wsgi
from django.contrib.auth.models import User
from analysis import models

import pandas as pd
import numpy as np
from datetime import datetime

df = pd.read_csv('final1.csv')

del df['Unnamed: 0']

df = df[22514:]
for index, row in df.iterrows():
    print "COUNT: ", index
    # create airline object
    airline = models.Airline.objects.filter(
        air_id=row['AIRLINE_ID'],
        carrier_code=row['UNIQUE_CARRIER']
    )
    if not airline:
        try:
            airline = models.Airline(
                air_id=row['AIRLINE_ID'],
                carrier_code=row['UNIQUE_CARRIER']
            )
            airline.save()
            print "Airline Object Created"
        except Exception as e:
            print str(e)
    else:
        airline = airline.first()
    
    # Create flight object
    air_flight = models.AirlineFlight.objects.filter(
        flight_no=row['FL_NUM'],
        airline=airline
    )
    if not air_flight:
        try:
            air_flight = models.AirlineFlight(
                flight_no=row['FL_NUM'],
                airline=airline
            )
            air_flight.save()
            print "Air_Flight Object Created"
        except Exception as e:
            print str(e)
    else:
        air_flight = air_flight.first()

    # create origin object
    origin = models.Airport.objects.filter(
        port_id = row['ORIGIN_AIRPORT_ID']
    )
    if not origin:
        try:
            origin = models.Airport(
                port_id=row['ORIGIN_AIRPORT_ID'],
                port_code=row['ORIGIN'],
                state_code=row['ORIGIN_STATE_ABR'],
                city_name=row['ORIGIN_CITY_NAME'],
                state_name=row['ORIGIN_STATE_NM']
            )
            origin.save()
            print "Origin Object Created"
        except Exception as e:
            print str(e)

    else:
        origin = origin.first()

    # create destination object
    dest = models.Airport.objects.filter(
        port_id = row['DEST_AIRPORT_ID']
    )

    if not dest:
        try:
            dest = models.Airport(
                port_id=row['DEST_AIRPORT_ID'],
                port_code=row['DEST'],
                state_code=row['DEST_STATE_ABR'],
                city_name=row['DEST_CITY_NAME'],
                state_name=row['DEST_STATE_NM']
            )
            dest.save()
            print "Destination Object Created"
        except Exception as e:
            print str(e)
    else:
        dest = dest.first()

    

    #create arrival performance object
    if row['CRS_ARR_TIME'] > 99 and row['CRS_ARR_TIME'] < 2400:
        crs_arr_time = datetime.strptime(str(row['CRS_ARR_TIME']), "%H%M")
    else:
        crs_arr_time = datetime.strptime("0000", "%H%M")
    
    if row['ARR_TIME'] > 99 and row['ARR_TIME'] < 2400:
        arr_time = datetime.strptime(str(row['ARR_TIME']), "%H%M")
    else:
        arr_time = datetime.strptime("0000", "%H%M")

    arr_perf = models.Performance.objects.filter(
        crs_time = crs_arr_time,
        actual_time = arr_time,
        delay = row['ARR_DELAY'],
        is_delay = row['ARR_DEL15'] == 1.0
    )
    if not arr_perf:
        try:
            arr_perf = models.Performance(
                crs_time = crs_arr_time,
                actual_time = arr_time,
                delay = row['ARR_DELAY'],
                is_delay = row['ARR_DEL15'] == 1.0
            )
            arr_perf.save()
        except Exception as e:
            print str(e)
    else:
        arr_perf = arr_perf.first()

    

    #create departure performance object
    if row['CRS_DEP_TIME'] > 99 and row['CRS_DEP_TIME'] < 2400:
        crs_dep_time = datetime.strptime(str(row['CRS_DEP_TIME']), "%H%M")
    else:
        crs_dep_time = datetime.strptime("0000", "%H%M")
    
    if row['DEP_TIME'] > 99 and row['DEP_TIME'] < 2400:
        dep_time = datetime.strptime(str(row['DEP_TIME']), "%H%M")
    else:
        dep_time = datetime.strptime("0000", "%H%M")

    dep_perf = models.Performance.objects.filter(
        crs_time = crs_dep_time,
        actual_time = dep_time,
        delay = row['DEP_DELAY'],
        is_delay = row['DEP_DEL15'] == 1.0
    )
    if not dep_perf:
        try:
            dep_perf = models.Performance(
                crs_time = crs_dep_time,
                actual_time = dep_time,
                delay = row['DEP_DELAY'],
                is_delay = row['DEP_DEL15'] == 1.0
            )
            dep_perf.save()
        except Exception as e:
            print str(e)
    else:
        dep_perf = dep_perf.first()

    #create trip object
    try:
        trip = models.Trip(
            air_flight=air_flight,
            origin=origin,
            destination=dest,
            arr_perf=arr_perf,
            dep_perf=dep_perf,
            crs_elapsed_time=row['CRS_ELAPSED_TIME'],
            actual_elapsed_time=row['ACTUAL_ELAPSED_TIME'],
            month=row['DAY_OF_MONTH'],
            week=row['DAY_OF_WEEK'],
            distance=row['DISTANCE'],
            tail_num=row['TAIL_NUM'],
            is_cancelled=row['CANCELLED'] == 1.0,
            cancel_code=row['CANCELLATION_CODE'],
            is_diverted=row['DIVERTED'] == 1.0
        )
        trip.save()
        print "Trip Object Created"
    except Exception as e:
        print str(e)

    #create delayed object
    delayed_obj = models.Delayed.objects.filter(trip=trip)
    if not delayed_obj and any( [row['CARRIER_DELAY'], 
            row['SECURITY_DELAY'],
            row['WEATHER_DELAY'],
            row['NAS_DELAY'],
            row['LATE_AIRCRAFT_DELAY']]
        ):
        try:
            models.Delayed(
                carrier=row['CARRIER_DELAY'],
                weather=row['WEATHER_DELAY'],
                nas=row['NAS_DELAY'],
                security=row['SECURITY_DELAY'],
                late_aircraft=row['LATE_AIRCRAFT_DELAY'],
                trip=trip
            ).save()
            print "Delayed Object Created"
        except Exception as e:
            print str(e)




