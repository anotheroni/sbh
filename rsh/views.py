# coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from sbh.rsh.forms import NewTaskForm
from sbh.rsh.models import Task, DayTask
from sbh.main.models import GasStation
from datetime import datetime, timedelta, date

@login_required()
def task_list(request, gid):
  gid = int(gid)
  today = date.today()
  # Try to get todays tasks
  task_list = DayTask.objects.filter(station = gid, date = today).order_by('time')
  if len(task_list) == 0: # No tasks today, try to create a list
    tasks = Task.objects.filter(Q(station = gid),
              Q(periodstart__isnull=True) | Q(periodstart__lte=today),
		      Q(periodend__isnull=True) | Q(periodend__gte=today))
    #raise Oskar
    # Weekday
    task_list =  []
    for task in tasks.filter(type = 1):
      task_list.append(task)
    # Day of week
    for task in tasks.filter(type = 2):
      if task.days[today.weekday()] != '0':
        task_list.append(task)
    # Day of month
#    task_list.append(tasks.filter(type = 3, day[day_of_monty]))

    # Create DayTasks for today
    for task in task_list:
      dt = DayTask(station=task.station, name=task.name, date=today, time=task.time)
      dt.save()
    try:
      task_list = DayTask.objects.filter(station = gid, date = today).order_by('time')
    except Task.DoesNotExist:	# No tasks today
      task_list = None

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
        type = int(cd['type'])
        repeat = int(cd ['repeat'])
        dayofm = int(cd ['dayofmonth'])
        task = Task.objects.get(station=gid, id=tid)
        task.name = cd['name']
        task.time = u"%s:00" % cd['time']
        task.periodstart = cd['periodstart']
        task.periodend = cd['periodend']
        task.type = type
        task.repeat = repeat
        task.dayofmonth = dayofm
        if type == 2:
          task.days = "%d%d%d%d%d%d%d" % (cd['daymon'], cd['daytue'],
                      cd['daywed'], cd['daythr'], cd['dayfri'], cd['daysat'],
                      cd['daysun'])
        elif type == 3:
          pass      
          
      except Task.DoesNotExist:
        task = Task(station=gs, name = cd['name'], time = u"%s:00" % cd['time'],
                    periodstart = cd['periodstart'], periodend = cd['periodend'],
                    type = int(cd['type']), repeat = int(cd['repeat']),
                    dayofmonth = int(cd['dayofmonth']), days = None)
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
  
  return render_to_response('rsh/task_management.html', c)

@login_required()
def sign_task(request, gid, tid):
  gid = int(gid)
  tid = int(tid)
  try:
    task = DayTask.objects.get(id = tid)
  except DayTask.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  
  task.signature = request.user
  task.timestamp = datetime.now()
  task.save()

  return HttpResponseRedirect(reverse('task_list', args=[gid]))
