# coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from sbh.rsh.forms import NewTaskForm
from sbh.rsh.models import Task
from sbh.main.models import GasStation

@login_required()
def task_list(request, gid):
  gid = int(gid)
  try:	# Make sure tasks exist, if not redirect
    task_list = Task.objects.filter(station = gid).order_by('time')
  except Task.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))

  c = RequestContext(request, {'object_list': task_list, 'gid': gid})
  return render_to_response('rsh/task_list.html', c)

# Also used to edit a task (tid != 0)
@login_required()
def newtask(request, gid, tid=0):
  gid = int(gid)
  tid = int(tid)
  try:  # Make sure Gas Station exists, if not redirect 
    gs = GasStation.objects.get(id = gid)
  except GasStation.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))

  if request.method == 'POST':
    form = NewTaskForm(gid, tid, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      try:
        task = Task.objects.get(station=gid, id=tid)
        task.name = cd['name']
        task.time = cd['time']
        task.periodstart = cd['periodstart']
        task.periodend = cd['periodend']
        task.type = int(cd['type'])
        task.repeat = int(cd['repeat'])
        task.dayofmonth = int(cd['dayofmonth'])
        task.mon = cd['daymon']
        task.tue = cd['daytue']
        task.wed = cd['daywed']
        task.thr = cd['daythr']
        task.fri = cd['dayfri']
        task.sat = cd['daysat']
        task.sun = cd['daysun']
      except Task.DoesNotExist:
        task = Task(station=gs, name = cd['name'], time = u"%s:00" % cd['time'],
                    periodstart = cd['periodstart'], periodend = cd['periodend'],
                    type = int(cd['type']), repeat = int(cd['repeat']),
                    dayofmonth = int(cd['dayofmonth']), mon = bool(cd['daymon']),
                    tue = bool(cd['daytue']), wed = bool(cd['daywed']),
                    thr = bool(cd['daythr']), fri = bool(cd['dayfri']),
                    sat = bool(cd['daysat']), sun = bool(cd['daysun']))
      task.save()
      return HttpResponseRedirect(reverse('task_management', args=[gid]))
  else:
    form = NewTaskForm(gid, tid)

  c = RequestContext(request, {'form': form, 'gid': gid})
  return render_to_response('rsh/newtask.html', c)

@login_required()
def task_management(request, gid):
  gid = int(gid)
  try:	# Make sure tasks exist, if not redirect
    task_list = Task.objects.filter(station = gid).order_by('name')
  except Task.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))

  c = RequestContext(request, {'object_list': task_list, 'gid': gid})
  return render_to_response('rsh/task_list.html', c)
