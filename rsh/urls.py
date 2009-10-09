from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^$', 'rsh.views.task_list', name="task_list"),
  url(r'^task/(?P<tid>\d+)/$', 'rsh.views.newtask', name="task"),
  url(r'^newtask/$', 'rsh.views.newtask', name="newtask"),
  url(r'^task_management/$', 'rsh.views.task_management', name="task_management"),
)
