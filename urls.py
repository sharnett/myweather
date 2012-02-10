from django.conf.urls.defaults import patterns, include, url
from myweatherapp.views import WeatherView

urlpatterns = patterns('',
    url(r'^$', WeatherView),
)
