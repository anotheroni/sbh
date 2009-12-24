# coding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from sbh.rsh.forms import NewTaskForm
from sbh.rsh.models import Task, DayTask
from sbh.main.models import GasStation, UserAuth
from datetime import datetime, timedelta, date

@login_required()
def task_list(request, gid):
  gid = int(gid)
  try: # Check user level for app
    uauth = UserAuth.objects.get(user = request.user, station = gid, app = 2)
  except UserAuth.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  if uauth.level < 1:
    return HttpResponseRedirect(reverse('program_list'))
  elif uauth.level > 1:
    adm = True
  else:
    adm = False

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
      # If repeat; get timedelta with the task start date and do modulus
      if task.repeat is None or ((today - task.periodstart).days % task.repeat == 0):
        task_list.append(task)
    # Day of week
    for task in tasks.filter(type = 2):
      try:
        # If repeat; get timedelta between first days of the weeks and do modulus
        if task.days[today.weekday()] != '0' and (task.repeat is None or
            ((today - task.periodstart - timedelta(today.weekday() -
              task.periodstart.weekday())).days / 7) % task.repeat == 0):
          task_list.append(task)
      except IndexError:
        pass
    # Day of month
    for task in tasks.filter(type = 3):
      try:
        # If repeat; calculate number of months between dates and do modulus
        if task.dayofmonth == today.day and (task.repeat is None or 
            ((today.year - task.periodstart.year) * 12 +
             today.month - task.periodstart.month) % task.repeat == 0):
          task_list.append(task)
      except IndexError:
        pass

    # Create DayTasks for today
    for task in task_list:
      dt = DayTask(station=task.station, name=task.name, date=today, time=task.time)
      dt.save()
    try:
      task_list = DayTask.objects.filter(station = gid, date = today).order_by('time')
    except Task.DoesNotExist:	# No tasks today
      task_list = None

  
  c = RequestContext(request, {'object_list': task_list, 'gid': gid, 'adm': adm})
  return render_to_response('rsh/task_list.html', c)

# Also used to edit a task (tid != 0)
@login_required()
def newtask(request, gid, tid=0):
  gid = int(gid)
  tid = int(tid)
  try: # Check user level for app
    uauth = UserAuth.objects.get(user = request.user, station = gid, app = 2)
  except UserAuth.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  if uauth.level < 2:
    return HttpResponseRedirect(reverse('program_list'))

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
        days = None
        dayofm = None
        if type == 2:
          days = "%d%d%d%d%d%d%d" % (cd['daymon'], cd['daytue'],
                      cd['daywed'], cd['daythr'], cd['dayfri'], cd['daysat'],
                      cd['daysun'])
        elif type == 3:
          dayofm = int(cd ['dayofmonth'])
      except ValueError:
        pass
      else:
        try:
          task = Task.objects.get(station=gid, id=tid)
          task.name = cd['name']
          task.time = u"%s:00" % cd['time']
          task.periodstart = cd['periodstart']
          task.periodend = cd['periodend']
          task.type = type
          task.repeat = repeat
          task.days = days
          task.dayofmonth = dayofm
        except Task.DoesNotExist:
          task = Task(station=gs, name = cd['name'], time = u"%s:00" % cd['time'],
                      periodstart = cd['periodstart'], periodend = cd['periodend'],
                      type = type, repeat = repeat, dayofmonth = dayofm, days = days)
        task.save()
        return HttpResponseRedirect(reverse('task_management', args=[gid]))
  else:
    form = NewTaskForm(gid, tid)

  c = RequestContext(request, {'form': form, 'gid': gid})
  return render_to_response('rsh/newtask.html', c)

@login_required()
def task_management(request, gid):
  gid = int(gid)
  try: # Check user level for app
    uauth = UserAuth.objects.get(user = request.user, station = gid, app = 2)
  except UserAuth.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  if uauth.level < 2:
    return HttpResponseRedirect(reverse('program_list'))
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
  try: # Check user level for app
    uauth = UserAuth.objects.get(user = request.user, station = gid, app = 2)
  except UserAuth.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  if uauth.level < 1:
    return HttpResponseRedirect(reverse('program_list'))

  try:
    task = DayTask.objects.get(id = tid, station = gid)
  except DayTask.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  
  task.signature = request.user
  task.timestamp = datetime.now()
  task.save()

  return HttpResponseRedirect(reverse('task_list', args=[gid]))
