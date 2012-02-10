from django.http import HttpResponse
from django.shortcuts import render_to_response
from get_json import *

def home(request):
    return HttpResponse("Hi there.")

def WeatherView(request):
    ds = ''
    params = dict((k, v) for k, v in request.GET.iteritems())
    if not params or not params['zip_code']:
        zip_code = 10025
    else:
        zip_code = int(params['zip_code']) 
    if not params or not params['num_hours']:
        num_hours = 8
    else:
        num_hours = int(params['num_hours'])
    w = weather_for_zip(zip_code)
    ds = get_shit_i_care_about(w, num_hours)
    return render_to_response('weather_form.html', \
            {'data_string': ds, 'zip_code': zip_code, 'num_hours': num_hours})
