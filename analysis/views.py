from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.shortcuts import redirect
from . import models
from django.db.models import Avg, F, FloatField, Sum
from django.db.models import Count

def login(request):
    context_dict = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password
        )
        if user is not None:
            return redirect('/ba-home')
        else:
            context_dict['message'] = "Incorrect Username or Password"
            return render(request, 'pages/login.html', context_dict)
    return render(request, 'pages/login.html', context_dict)


def register(request):
    context_dict = {}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        user = User.objects.filter(username=username)
        if not user:
            try:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                return redirect('/ba-home')
            except Exception as e:
                print str(e)
        else:
            context_dict['message'] = "username already taken"
            context_dict['username'] = username
            context_dict['email'] = email
            return render(request, 'pages/register.html', context_dict)
    return render(request, 'pages/register.html', context_dict)

def ba_home(request):
    return render(request, 'pages/bairports.html')


def busiest_airports(request):
    context_dict = {}
    airports = models.Airport.objects.filter(
        state_code='CA'
    )
    res = []
    for port in airports:
        temp = []
        temp.append(port.port_code)
        count = models.Trip.objects.filter(
            origin=port,
        ).count()
        + models.Trip.objects.filter(
            destination=port,
        ).count()
        temp.append(count)
        res.append(temp)
    labels = []
    values = []
    res = sorted(res, key=lambda x:x[1], reverse=True)[:10]
    for i in res:
        labels.append(i[0])
        values.append(i[1])
    context_dict['labels'] = labels
    context_dict['values'] = values
    return JsonResponse(context_dict)

def br_home(request):
    context_dict = {}
    context_dict['airlines'] = models.Airline.objects.values_list(
        'carrier_code',
        flat=True
    )
    context_dict['states'] = models.Airport.objects.values_list(
        'state_code',
        flat=True
    ).distinct()
    return render(request, 'pages/broutes.html', context_dict)


def busiest_routes(request):
    context_dict = {}
    state1 = request.GET.get('state1', 'CA')
    state2 = request.GET.get('state2', 'CA')
    airline = request.GET.get('airline', '')
    airports1 = models.Airport.objects.filter(state_code=state1)
    airports2 = models.Airport.objects.filter(state_code=state2)
    res = []
    for i in range(len(airports1)):
        j = i+1
        while j<len(airports2):
            print "count", len(res)
            temp = []
            route_name = airports1[i].port_code+'-'+airports2[j].port_code
            if not airline or airline == 'all':
                count = models.Trip.objects.filter(
                    origin=airports1[i],
                    destination=airports2[j]
                ).count()
                + models.Trip.objects.filter(
                    origin=airports2[j],
                    destination=airports1[i]
                ).count()
            else:
                count = models.Trip.objects.filter(
                    origin=airports1[i],
                    destination=airports2[j],
                    air_flight__airline__carrier_code=airline
                ).count()
                + models.Trip.objects.filter(
                    origin=airports2[j],
                    destination=airports1[i],
                    air_flight__airline__carrier_code=airline
                ).count()
            temp.append(route_name)
            temp.append(count)
            res.append(temp)
            j += 1
    res = sorted(res, key=lambda x:x[1], reverse=True)[:10]
    labels = []
    values = []
    for i in res:
        labels.append(i[0])
        values.append(i[1])
    context_dict['labels'] = labels
    context_dict['values'] = values
    return JsonResponse(context_dict)


def perf_home(request):
    context_dict = {}
    context_dict['airlines'] = models.Airline.objects.values_list('carrier_code', flat=True)
    return render(request, 'pages/performance.html', context_dict)


def performance(request):
    context_dict = {}
    av1, dv1, anum1, dnum1, av2, dv2, anum2, dnum2 = [], [], [], [], [], [], [], []
    a = models.Trip.objects.all()
    c = models.Trip.objects.filter(arr_perf__is_delay=True)
    d = models.Trip.objects.filter(dep_perf__is_delay=True)
    if request.GET.get('airline1'):
        a1_id = request.GET.get('airline1')
        a1 = a.filter(air_flight__airline__carrier_code=a1_id)
        c1 = c.filter(air_flight__airline__carrier_code=a1_id)
        d1 = d.filter(air_flight__airline__carrier_code=a1_id)
    if request.GET.get('airline1'):
        a2_id = request.GET.get('airline2')
        a2 = a.filter(air_flight__airline__carrier_code=a2_id)
        c2 = c.filter(air_flight__airline__carrier_code=a2_id)
        d2 = d.filter(air_flight__airline__carrier_code=a2_id)
    for i in range(1, 32, 8):
        av1.append(a1.filter(
            month__lt=i+8,
            month__gte=i
        ).aggregate(
        Avg('arr_perf__delay')
        )['arr_perf__delay__avg'])
        av2.append(a2.filter(
            month__lt=i+8,
            month__gte=i
        ).aggregate(
        Avg('arr_perf__delay')
        )['arr_perf__delay__avg'])

        dv1.append(a1.filter(
            month__lt=i+8,
            month__gte=i
        ).aggregate(
        Avg('dep_perf__delay')
        )['dep_perf__delay__avg'])

        dv2.append(a2.filter(
            month__lt=i+8,
            month__gte=i
        ).aggregate(
        Avg('dep_perf__delay')
        )['dep_perf__delay__avg'])

        anum1.append(
            c1.filter(
                month__lt=i+8,
                month__gte=i
            ).count()
        )
        dnum1.append(
            d1.filter(
                month__lt=i+8,
                month__gte=i
            ).count()
        )

        anum2.append(
            c2.filter(
                month__lt=i+8,
                month__gte=i
            ).count()
        )

        dnum2.append(
            d2.filter(
                month__lt=i+8,
                month__gte=i
            ).count()
        )
    context_dict['labels'] = [1,2,3,4]
    context_dict['av1'] = av1
    context_dict['dv1'] = dv1
    context_dict['anum1'] = anum1
    context_dict['dnum1'] = dnum1
    context_dict['av2'] = av2
    context_dict['dv2'] = dv2
    context_dict['anum2'] = anum2
    context_dict['dnum2'] = dnum2
    context_dict['airline1'] = a1_id
    context_dict['airline2'] = a2_id
    return JsonResponse(context_dict)


def delayed_flights(request):
    context_dict = {}
    carrier = request.POST.get('airline', 'HA')
    if carrier == 'all':
        airlines = models.Airline.objects.all()
    else:
        airlines = models.Airline.objects.filter(carrier_code=carrier)    
    big_dict = {}
    context_dict['airlines'] = models.Airline.objects.values_list(
        'carrier_code', flat=True
    )
    for airline in airlines:
        my_dict={}
        flights = models.AirlineFlight.objects.filter(
            airline=airline
        )
        for flight in flights:
            ftrips = models.Trip.objects.filter(
                air_flight=flight
            ).values_list('id', flat=True)
            delayed_trips = models.Delayed.objects.filter(
                trip__id__in=ftrips
            ).values_list('trip__id', flat=True)
            if len(delayed_trips) > 10:
                dtrips = models.Trip.objects.filter(id__in=delayed_trips)
                avg_arr_delay = int(dtrips.aggregate(
                    Avg('arr_perf__delay')
                )['arr_perf__delay__avg'])
                avg_dep_delay = int(dtrips.aggregate(
                    Avg('dep_perf__delay')
                )['dep_perf__delay__avg'])
                my_dict[flight.flight_no] = [len(delayed_trips), avg_arr_delay, avg_dep_delay]

        big_dict[airline.carrier_code] = my_dict
            
    context_dict['data'] = big_dict
    return render(request, 'pages/delayed_flights.html', context_dict)


def flight_desc(request):
    context_dict = {}
    af = request.GET.get('airflight')
    af = af.split('-')
    airline = models.Airline.objects.get(carrier_code=af[0])
    aflight = models.AirlineFlight.objects.get(
        airline=airline, 
        flight_no=af[1]
    )
    trips = models.Trip.objects.filter(air_flight=aflight)
    arr = trips[0].arr_perf.crs_time.strftime("%H%M")
    dep = trips[0].dep_perf.crs_time.strftime("%H%M")
    org = trips[0].origin
    dest = trips[0].destination
    try:
        temp = trips.filter(origin=dest, destination=org).first()
        context_dict['arr2'] = temp.arr_perf.crs_time.strftime("%H%M")
        context_dict['dep2'] = temp.dep_perf.crs_time.strftime("%H%M")
        context_dict['route2'] = dest.port_code+'-'+org.port_code
    except Exception as e:
        print str(e)
        context_dict['arr2'] = ''
        context_dict['dep2'] = ''
        context_dict['route2'] = ''
    context_dict['airline'] = af[0]
    context_dict['flight_no'] = af[1]
    context_dict['arr1'] = arr
    context_dict['dep1'] = dep
    context_dict['route1'] = org.port_code+'-'+dest.port_code
    context_dict['labels'] = ["MON", "TUE", "WED", "THUR", "FRI", "SAT", "SUN"]
    context_dict['avalues1'] = []
    context_dict['dvalues1'] = []
    context_dict['avalues2'] = []
    context_dict['dvalues2'] = []
    tr1 = trips.filter(origin=org, destination=dest)
    tr2 = trips.filter(origin=dest, destination=org)
    for i in range(1, 8):
        t = tr1.filter(week=i)
        if t:
            avg_arr_delay = t.aggregate(Avg('arr_perf__delay'))
            avg_dep_delay = t.aggregate(Avg('dep_perf__delay'))
            context_dict['avalues1'].append(
                int(avg_arr_delay['arr_perf__delay__avg'])
            )
            context_dict['dvalues1'].append(
                int(avg_dep_delay['dep_perf__delay__avg'])
            )
        else:
            context_dict['avalues1'].append(0)
            context_dict['dvalues1'].append(0)

    for i in range(1, 8):
        t = tr2.filter(week=i)
        if t:
            avg_arr_delay = t.aggregate(Avg('arr_perf__delay'))
            avg_dep_delay = t.aggregate(Avg('dep_perf__delay'))
            context_dict['avalues2'].append(
                int(avg_arr_delay['arr_perf__delay__avg'])
            )
            context_dict['dvalues2'].append(
                int(avg_dep_delay['dep_perf__delay__avg'])
            )
        else:
            context_dict['avalues2'].append(0)
            context_dict['dvalues2'].append(0)

    return JsonResponse(context_dict)


def delayed_percent(request):
    context_dict = {}
    state = request.POST.get('state', 'IL')
    cause = request.POST.get('cause', 'weather')
    direction = request.POST.get('direction', 'i')
    context_dict['states'] = models.Airport.objects.values_list(
        'state_code',
        flat=True
    )
    context_dict['causes'] = ['weather', 'nas', 'security', 'late_aircraft', 'carrier']
    airlines = models.Airline.objects.values_list(
        'carrier_code',
        flat=True
    )
    context_dict['airlines'] = airlines
    if state == 'all':
        states = context_dict['states']
    else:
        states = [state]

    big_dict = {}
    for state in states:
        my_dict = {}
        for airline in airlines:
            print airline
            flights = models.AirlineFlight.objects.filter(
                airline__carrier_code=airline
            )
            ftrips = models.Trip.objects.filter(
                air_flight__in=flights
            )
            if direction == 'i':
                ftrips = ftrips.filter(destination__state_code=state)
            else:
                ftrips = ftrips.filter(origin__state_code=state)
            delayed_trips = models.Delayed.objects.filter(
                trip__in=ftrips
            )
            w = float(sum(delayed_trips.values_list('weather', flat=True)))
            if not w:
                w = 0
            n = float(sum(delayed_trips.values_list('nas', flat=True)))
            if not n:
                n = 0
            s = float(sum(delayed_trips.values_list('security', flat=True)))
            if not s:
                s = 0
            la = float(sum(delayed_trips.values_list('late_aircraft', flat=True)))
            if not la:
                la = 0
            c = float(sum(delayed_trips.values_list('carrier', flat=True)))
            if not c:
                c = 0
            
            total = w + n + s + la + c
            if total:
                percentw = round((w/total)*100,2)
                percentn = round((n/total)*100,2)
                percents = round((s/total)*100,2)
                percentla = round((la/total)*100,2)
                percentc = round((c/total)*100,2)
                my_dict[airline] = [percentw, percentn, percents, percentla, percentc]
        big_dict[state] = my_dict
    context_dict['data'] = big_dict
    print big_dict
    return render(request, 'pages/delayed_percent.html', context_dict)

def aprof_home(request):
    context_dict = {}
    context_dict['airlines'] = models.Airline.objects.values_list(
        'carrier_code',
        flat=True
    )
    return render(request, 'pages/aprofile.html', context_dict)


def airline_profile(request):
    context_dict = {}
    airline = request.GET.get('airline', 'AA')
    airline = models.Airline.objects.get(carrier_code=airline)

    div = models.Trip.objects.filter(
        is_diverted=True,
        air_flight__airline=airline
    ).count()

    canc = models.Trip.objects.filter(
        is_cancelled=True,
        air_flight__airline=airline
    ).count()

    ad = models.Trip.objects.filter(
        arr_perf__is_delay=True
    ).count()

    dd = models.Trip.objects.filter(
        dep_perf__is_delay=True
    ).count()

    context_dict['perf'] = [div, canc, ad, dd]
    states = models.Airport.objects.values_list(
        'state_code',
        flat=True
    ).distinct()
    print len(states)
    incoming = []
    outgoing = []
    slabels = []
    for state in states:
        oc = models.Trip.objects.filter(
            air_flight__airline=airline,
            origin__state_code=state
        ).count()
        outgoing.append(oc)
        ic = models.Trip.objects.filter(
            air_flight__airline=airline,
            destination__state_code=state
        ).count()
        slabels.append(state)
        incoming.append(ic)

    context_dict['incoming'] = incoming
    context_dict['outgoing'] = outgoing
    context_dict['slabels'] = slabels

    air_flights = models.AirlineFlight.objects.filter(
        airline = airline
    )
    flight_density = []
    flabels = []
    fd = []
    for af in air_flights:
        trip_count = models.Trip.objects.filter(
            air_flight=af
        ).count()
        fd.append([af.flight_no, trip_count])

    res = sorted(fd, key=lambda x:x[1], reverse=True)[:10]
    flabels = []
    flight_density = []
    for i in res:
        flabels.append(i[0])
        flight_density.append(i[1])

    context_dict['fd'] = flight_density
    context_dict['flabels'] = flabels
    print len(slabels)
    return JsonResponse(context_dict)


























