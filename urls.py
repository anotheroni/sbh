from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^pin/', include('sbh.pin.urls')),
    (r'^accounts/$', login), # {'template_name': 'pin/login.html'}),
    (r'^accounts/login/$', login), # {'template_name': 'pin/login.html'}),
    (r'^accounts/logout/$', logout), #, {'template_name': 'pin/logout.html'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/(.*)', admin.site.root),
)
