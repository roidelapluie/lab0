from django.conf.urls import patterns, include, url
from backend.api import api_v1

from django.views.generic import RedirectView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include(api_v1.urls)),
    url(r'^$', RedirectView.as_view(url='static/index.html')),
    url(r'^admin/', include(admin.site.urls)),
)
