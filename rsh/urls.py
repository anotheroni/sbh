from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^(?P<gid>\d+)/$', 'rsh.views.task_list', name="task_list"),
  url(r'^(?P<gid>\d+)/task/(?P<tid>\d+)/$', 'rsh.views.newtask', name="task"),
  url(r'^(?P<gid>\d+)/newtask/$', 'rsh.views.newtask', name="newtask"),
  url(r'^(?P<gid>\d+)/task_management/$', 'rsh.views.task_management', name="task_management"),
  url(r'^(?P<gid>\d+)/sign_task/(?P<tid>\d+)/$', 'rsh.views.sign_task', name="sign_task"),
)
