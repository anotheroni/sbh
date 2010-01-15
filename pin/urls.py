from django.conf.urls.defaults import *

urlpatterns = patterns('',
#  url(r'^$', 'pin.views.station_list', name="station_list"),
  url(r'^(?P<gid>\d+)/report_list/$', 'pin.views.report_list', name="report_list"),
  url(r'^(?P<gid>\d+)/report_list/(?P<year>\d{4})/$', 'pin.views.report_list', name="report_list"),
  url(r'^(?P<gid>\d+)/report_list/(?P<year>\d{4})/(?P<month>\w{3})/$', 'pin.views.report_list', name="report_list"),
  url(r'^(?P<gid>\d+)/new_report/$', 'pin.views.new_report', name="new_report"),
  url(r'^report/(?P<rid>\d+)/$', 'pin.views.overview_report', name="overview_report"),
  url(r'^report/(?P<rid>\d+)/mech/$', 'pin.views.mech_report', name="mech_report"),
  url(r'^report/(?P<rid>\d+)/deliv/$', 'pin.views.deliv_report', name="delivery_report"),
  url(r'^report/(?P<rid>\d+)/del_deliv/d(?P<did>\d+)/$', 'pin.views.delete_delivery', name="delivery_delete"),
  url(r'^report/(?P<rid>\d+)/misc/$', 'pin.views.misc_report', name="misc_report"),
  url(r'^report/(?P<rid>\d+)/view/$', 'pin.views.view_report', name="view_report"),
)
