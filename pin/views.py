from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from sbh.pin.models import Report, GasStation, PumpStatus, Delivery, FuelTypeData, FuelType, PumpNozle
#from sbh.pin.forms import get_mechanical_meter_form
from sbh.pin.forms import MechanicalMeterForm, DeliveryForm, MiscForm
from datetime import datetime

@login_required() #redirect_field_name='login/') #?next=%s' % request.path)
def station_list(request):
  station_list = GasStation.objects.all().order_by('name')
  c = RequestContext(request, {'object_list': station_list})
  return render_to_response('pin/station_list.html', c)


@login_required()
def report_list(request, gid=0):
  gid = int(gid)
  try:	# Make sure that the Gas Station exists, if not redirect 
    gs = GasStation.objects.get(id = gid)
  except GasStation.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  report_list = Report.objects.filter(station=gid).order_by('-date')
  c = RequestContext(request, {'object_list': report_list, 'gid': gid})
  return render_to_response('pin/report_list.html', c)

@login_required()
def new_report(request, gid = 0):
  gid = int(gid)
  try:  # Make sure that the Gas Station exists, if not redirect 
    gs = GasStation.objects.get(id = gid)
  except GasStation.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))
  
  try:  # Check if there is an unsigned report to continue
    r = Report.objects.get(station = gid, signature__isnull = True)
  except Report.DoesNotExist:
    try:  # find which is the next date to report
      rep = Report.objects.get(station = gid).order_by('-date')[0:1]
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
  return render_to_response('pin/overview_report.html', c)
  

@login_required()
def mech_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))
    
  if request.method == 'POST':
    form = MechanicalMeterForm(gs=rep.station, data=request.POST)
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
    form = MechanicalMeterForm(gs=rep.station)

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
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  if request.method == 'POST':
    form = MiscForm(gs = rep.station, data = request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      for ft_id,name in GasStation.get_used_fuel_types(rep.station):
        # TODO check if record exists
        ftdo = FuelTypeData(report = rep, fuel_type = FuelType.objects.get(id = ft_id),
                 accumulated_storage_diff = 00.00,
                 accumulated_sold = 00.00,
                 elec_meter_reading = float(cd['elec_%d' % ft_id]),
                 elec_accumulated_diff = 00.00,
                 pin_meter_reading = float(cd['pin_%d' % ft_id]),
                 rundp_data = float(cd['rp_%d' % ft_id]),
                 pumpp_data = float(cd['pp_%d' % ft_id]))
        ftdo.save()
      return HttpResponseRedirect('/pin/new_report/r%d/ov/' % rid)
  else:
    form = MiscForm(gs=rep.station)

  ft_list = GasStation.get_used_fuel_types(rep.station)

  c = RequestContext(request, {'gid': rep.station, 'form': form, 'ft_list': ft_list})
  return render_to_response('pin/misc_report.html', c)

@login_required()
def view_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('pin.views.station_list'))

  ft_list = GasStation.get_used_fuel_types(rep.station)
  page = list()
  row00 = ["#"]
  row10 = ["S:a matarstallning idag"]
  row15 = ["Avlasning registerinstallning idag"]
  row28 = ["Pejlat lager idag"]
  row32 = ["Rundpumpning"]
  row41 = ["Pumppris idag"]

  pumpnumlist = list()
  pumprowlist = list()
  pumpop = dict()
  for pump in PumpStatus.objects.filter(report = rep):
    pump_num = pump.pump_nozle.pump.number
    if pump_num not in pumpnumlist:
      pumpnumlist.append(pump_num)
    pumpop["pump_%d_%d" % (pump_num, pump.pump_nozle.fuel_type.id)] = pump.meter_reading
  pumpnumlist.sort()
  for pump_num in pumpnumlist:
    pumprowlist.append(["%d" % pump_num])

  for ft_id,ft_name in ft_list:
    row00.append(ft_name)
    ftdo = FuelTypeData.objects.get(report = rep, fuel_type = ft_id)

    pump_tot = 0.0
    for prl in pumprowlist:
      try:
        val = pumpop["pump_%s_%d" % (prl[0], ft_id)]
        pump_tot = pump_tot + val
        prl.append(val)
      except:
        prl.append("")
    row10.append(pump_tot)

    row15.append(ftdo.elec_meter_reading)
    row28.append(ftdo.pin_meter_reading)
    row32.append(ftdo.rundp_data)
    row41.append(ftdo.pumpp_data)

  page.append(row00)
  page = page + pumprowlist
  page.append(row10)
  page.append(row15)
  page.append(row28)
  page.append(row32)
  page.append(row41)

  c = RequestContext(request, {'gid': rep.station, 'page': page})
  return render_to_response('pin/view_report.html', c)

