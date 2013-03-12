from django.conf.urls.defaults import patterns, include, url
from myweatherapp.views import WeatherView, LunchView

urlpatterns = patterns('',
    url(r'^$', WeatherView),
    url(r'^lunch/$', LunchView.as_view()),
)
