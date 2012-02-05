from django.conf.urls.defaults import patterns, include, url
from myweatherapp.views import WeatherView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', WeatherView),
    url(r'^admin/', include(admin.site.urls)),
)
