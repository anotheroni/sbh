# coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from sbh.rsh.forms import NewEventForm
from sbh.rsh.models import Event

@login_required()
def task_list(request, gid=0):
  gid = int(gid)
  try:	# Make sure report exist, if not redirect
    event = Event.objects.filter(id = gid)
  except Event.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

@login_required()
def newtask(request, gid=0, tid=0):
  gid = int(gid)
  tid = int(tid)

  if request.method == 'POST':
    form = NewEventForm(tid, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      event = Event()
      event.save()
      return HttpResponseRedirect(reverse('taks_management'))
  else:
    form = NewEventForm(tid)

  c = RequestContext(request, {'form': form})
  return render_to_response('rsh/newtask.html', c)

@login_required()
def task_management(request, gid=0):
  gid = int(gid)
  try:	# Make sure report exist, if not redirect
    event_list = Event.objects.filter(station = gid).order_by('name')
  except Event.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

  c = RequestContext(request, {'object_list': event_list, 'gid': gid})
  return render_to_response('rsh/event_list.html', c)
