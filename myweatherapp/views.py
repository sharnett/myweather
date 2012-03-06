from django.shortcuts import render_to_response
from get_json import *

def WeatherView(request):
    params = dict((k, v) for k, v in request.GET.iteritems())
    if not params or not params['zip_code']:
        if request.COOKIES.has_key('zip_code'):
            zip_code = int(request.COOKIES['zip_code'])
        else:
            zip_code = 10025
    else:
        zip_code = int(params['zip_code']) 
    if not params or not params['num_hours']:
        if request.COOKIES.has_key('num_hours'):
            num_hours = int(request.COOKIES['num_hours'])
        else:
            num_hours = 12
    else:
        num_hours = int(params['num_hours'])
    w = weather_for_zip(zip_code)
    ds = get_shit_i_care_about(w, num_hours)
    response = render_to_response('weather_form.html', \
            {'data_string': ds, 'zip_code': zip_code, 'num_hours': num_hours})
    response.set_cookie('zip_code', zip_code, max_age=365*24*68*68)
    response.set_cookie('num_hours', num_hours, max_age=365*24*68*68)
    return response
