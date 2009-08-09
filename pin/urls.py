from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^$', 'pin.views.station_list'),
  (r'^report_list/$', 'pin.views.report_list'),
  (r'^report_list/(?P<gid>\d+)/$', 'pin.views.report_list'),
  (r'^new_report/$', 'pin.views.new_report'),
  (r'^new_report/(?P<gid>\d+)/$', 'pin.views.new_report'),
  (r'^new_report/r(?P<rid>\d+)/$', 'pin.views.overview_report'),
  (r'^new_report/r(?P<rid>\d+)/mech/$', 'pin.views.mech_report'),
  (r'^new_report/r(?P<rid>\d+)/deliv/$', 'pin.views.deliv_report'),
  (r'^new_report/r(?P<rid>\d+)/del_deliv/d(?P<did>\d+)/$', 'pin.views.delete_delivery'),
  (r'^new_report/r(?P<rid>\d+)/misc/$', 'pin.views.misc_report'),
  (r'^new_report/r(?P<rid>\d+)/view/$', 'pin.views.view_report'),
  (r'^report/(?P<gid>\d+)/$', 'pin.views.view_report'),
)

