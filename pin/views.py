from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from sbh.pin.models import Report, GasStation, PumpStatus, Delivery, AccumulatedData, FuelType, PumpNozle
#from sbh.pin.forms import get_mechanical_meter_form
from sbh.pin.forms import MechanicalMeterForm, DeliveryForm
from datetime import datetime

@login_required() #redirect_field_name='login/') #?next=%s' % request.path)
def station_list(request):
  station_list = GasStation.objects.all().order_by('name')
  c = RequestContext(request, {'object_list': station_list})
  return render_to_response('pin/station_list.html', c)


@login_required()
def report_list(request, gid=0):
  try:	# Make sure that the Gas Station exists, if not redirect 
    gs = GasStation.objects.get(id = int(gid))
  except GasStation.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  report_list = Report.objects.filter(station=int(gid)).order_by('-date')
  c = RequestContext(request, {'object_list': report_list, 'gid': gid})
  return render_to_response('pin/report_list.html', c)

@login_required()
def new_report(request, gid = 0):
  try:  # Make sure that the Gas Station exists, if not redirect 
    gs = GasStation.objects.get(id = int(gid))
  except GasStation.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))
  
  try:  # Check if there is an unsigned report to continue
    r = Report.objects.get(station = int(gid), signature__isnull = True)
  except Report.DoesNotExist:
    try:  # find which is the next date to report
      rep = Report.objects.get(station = int(gid)).order_by('-date')[0:1]
      date = rep.date + timedelta(days=1)
    except Report.DoesNotExist:  # This is the first report for the station!
      date = datetime.today()
    r = Report(date = date, station = gs)
    r.save()
  
  return HttpResponseRedirect('/pin/new_report/r%d/ov' % r.id)
#reverse('pin.views.overview_report', args=[r.id, 'ov']))

@login_required()
def overview_report(request, rid=0):
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = int(rid))
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  c = RequestContext(request, {'report': rep})
#, 'report_has_mech_data': rep.has_mech_data(), 'report_is_complete': rep.is_complete()})
  return render_to_response('pin/overview_report.html', c)
  

@login_required()
def mech_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))
    
  if request.method == 'POST':
    form = MechanicalMeterForm(gid=rep.station, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      for data in cd:
        try:  # TODO check earlier
          pn = PumpNozle.objects.get(id = data)
        except PumpNozle.DoesNotExist:
          pass
        else:
          ps = PumpStatus(report = rep, pump_nozle = pn, meter_reading = cd[data])
          ps.save()
      return HttpResponseRedirect('/pin/new_report/r%d/ov/' % rid)
  else:
    form = MechanicalMeterForm(gid=rep.station)

  c = RequestContext(request, {'gid': rep.station, 'form': form})
  return render_to_response('pin/mech_report.html', c)

@login_required()
def deliv_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  if request.method == 'POST':
    form = DeliveryForm(gs=rep.station, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      try:
        ft = FuelType.objects.get(id = int(cd['type']))
      except FuelType.DoesNotExist:
        # TODO update form is_valid check
        return HttpResponseRedirect('/pin/new_report/r%d/ov/' % rid)
      deliv = Delivery(report = rep, fuel_type = ft, station = rep.station , volume = cd['amount'])
      deliv.save()
      return HttpResponseRedirect('/pin/new_report/r%d/ov/' % rid)
  else:
    form = DeliveryForm(gs=rep.station)

  deliveries = Delivery.objects.filter(report = rid)

  c = RequestContext(request, {'gid': rep.station, 'form': form, 'object_list': deliveries})
  return render_to_response('pin/deliv_report.html', c)

@login_required()
def misc_report(request, rid=0):
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = int(rid))
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  c = requestcontext(request, {'gid': gid, 'form': form})
  return render_to_response('pin/misc_report.html', c)

@login_required()
def view_report(request, rid=0):
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = int(rid))
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  c = requestcontext(request, {'gid': gid, 'form': form})
  return render_to_response('pin/misc_report.html', c)

