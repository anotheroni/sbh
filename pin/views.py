# coding: utf-8
import re   # regexp
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from sbh.main.models import GasStation, UserAuth
from sbh.pin.models import Report, Pump, PumpStatus, Delivery, FuelTypeData, FuelType, PumpNozle, get_used_fuel_types
from sbh.pin.forms import MechanicalMeterForm, DeliveryForm, MiscForm, ViewReportForm
from datetime import datetime, timedelta
from copy import copy

from django.views.generic.date_based import archive_index, archive_year, archive_month

#@login_required() #redirect_field_name='login/') #?next=%s' % request.path)
#def station_list(request):
#  station_list = GasStation.objects.all().order_by('name')
#  c = RequestContext(request, {'object_list': station_list})
#  return render_to_response('pin/station_list.html', c)

@login_required()
def report_list(request, gid=0, year=0):
  gid = int(gid)
  try: # Check user level for app
    uauth = UserAuth.objects.get(user = request.user, station = gid, app = 1)
  except UserAuth.DoesNotExist:
    return HttpResponseRedirect(reverse('program_list'))
  if uauth.level < 1:
    return HttpResponseRedirect(reverse('program_list'))

  try:  # Check if there is an unsigned report. Needed for view.
    Report.objects.get(station=gid, signature=None)
    unsignedreport = True
  except Report.DoesNotExist:
    unsignedreport = False

  if month is not None:
      # month view
    #return archive_month(request, queryset=)
  elif year is not None:
      # year view
  else
      # archive view

  report_list = Report.objects.filter(station=gid).order_by('date')
  c = RequestContext(request, {'object_list': report_list, 'gs': uauth.station,
                               'unsignedreport': unsignedreport})
  return render_to_response('pin/report_list.html', c)

@login_required()
def new_report(request, gid = 0):
  gid = int(gid)
  try:  # Make sure that the Gas Station exists, if not redirect 
    gs = GasStation.objects.get(id = gid)
  except GasStation.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))
  
  try:  # Check if there is an unsigned report to continue
    r = Report.objects.get(station = gid, signature__isnull = True)
  except Report.DoesNotExist:
    # find which is the next date to report
    rep = Report.objects.filter(station = gid).order_by('-date')[0:1]
    try:
      date = rep[0].date + timedelta(days=1)
      r = Report(date = date, station = gs, previous = rep[0].id)
    except IndexError:  # This is the first report for the station!
      r = Report(date = datetime.today(), station = gs, previous = None)
    r.save()
  
  return HttpResponseRedirect(reverse('overview_report', args=[r.id]))

@login_required()
def overview_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

  c = RequestContext(request, {'rep': rep})
  return render_to_response('pin/overview_report.html', c)
  

@login_required()
def mech_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))
    
  if request.method == 'POST':
    form = MechanicalMeterForm(rep=rep, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      ft_dict = dict()
      # Create dict with fuel type totals 
      for ft_id, name in get_used_fuel_types(rep.station.id):
        ft_dict[ft_id] = 0.0
      # Iterat all fields
      for name, val in cd.items():
        try:
          m = re.search('^(\d+)_(\d+)$', name)
          pn = PumpNozle.objects.get(pump = m.group(1), fuel_type=m.group(2))
        except PumpNozle.DoesNotExist:
          continue
        else:
          try:
            ps = PumpStatus.objects.get(report = rep, pump_nozle = pn)
            ps.meter_reading = val
          except:
            ps = PumpStatus(report = rep, pump_nozle = pn, meter_reading = val)
          ft_dict[pn.fuel_type.id] = ft_dict[pn.fuel_type.id] + val
          ps.save()

      for id,val in ft_dict.iteritems():  # Save fuel_type total 
        ft = FuelType.objects.get(id=id)
        try:  # If data already exists update
          ftd = FuelTypeData.objects.get(report = rep, fuel_type = ft)
          ftd.mech_total_today = val
        except: # Otherwise create it
          ftd = FuelTypeData(report = rep, fuel_type = ft, mech_total_today = val)
        ftd.save()

      return HttpResponseRedirect(reverse('overview_report', args=[rid]))
  else:
    form = MechanicalMeterForm(rep=rep)

  #for name, field in form.fields.items():
    #bf = BoundField(form, field, name)


  c = RequestContext(request, {'rep': rep, 'form': form})
  return render_to_response('pin/mech_report.html', c)

@login_required()
def deliv_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

  if request.method == 'POST':
    form = DeliveryForm(gs=rep.station, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      try:
        ft = FuelType.objects.get(id = int(cd['type']))
      except FuelType.DoesNotExist:
        # TODO update form is_valid check
        return HttpResponseRedirect(reverse('delivery_report', args=[rid]))
      deliv = Delivery(report = rep, fuel_type = ft, station = rep.station , volume = cd['amount'])
      deliv.save()
      return HttpResponseRedirect(reverse('delivery_report', args=[rid]))
  else:
    form = DeliveryForm(gs=rep.station)

  deliveries = Delivery.objects.filter(report = rid)
  o_list = list()
  for d in deliveries:
    x = (d.fuel_type.name, d.volume)

  c = RequestContext(request, {'rep': rep, 'form': form, 'object_list': deliveries})
  return render_to_response('pin/deliv_report.html', c)

@login_required()
def delete_delivery(request, rid=0, did=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

  try:
    delivery = Delivery.objects.get(id = did)
    delivery.delete()
  except Delivery.DoesNotExist:
    pass

  return HttpResponseRedirect(reverse('delivery_report', args=[rid]))


@login_required()
def misc_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

  if request.method == 'POST':
    form = MiscForm(rep = rep, data = request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      for ft_id,name in get_used_fuel_types(rep.station.id):
        fto = FuelType.objects.get(id = ft_id)
        try:
          ftdo = FuelTypeData.objects.get(report = rep, fuel_type = fto)
          ftdo.elec_meter_reading = float(cd['elec_%d' % ft_id])
          ftdo.pin_meter_reading = float(cd['pin_%d' % ft_id])
          ftdo.rundp_data = float(cd['rp_%d' % ft_id])
          ftdo.pumpp_data = float(cd['pp_%d' % ft_id])
        except FuelTypeData.DoesNotExist:
          ftdo = FuelTypeData(report = rep, fuel_type = fto,
                 elec_meter_reading = float(cd['elec_%d' % ft_id]),
                 pin_meter_reading = float(cd['pin_%d' % ft_id]),
                 rundp_data = float(cd['rp_%d' % ft_id]),
                 pumpp_data = float(cd['pp_%d' % ft_id]))
        ftdo.save()
      return HttpResponseRedirect(reverse('overview_report', args=[rid]))
    else:
      pass  # TODO propper error handling
  else:
    form = MiscForm(rep=rep)

  ft_list = get_used_fuel_types(rep.station.id)

  c = RequestContext(request, {'rep': rep, 'form': form, 'ft_list': ft_list})
  return render_to_response('pin/misc_report.html', c)

@login_required()
def view_report(request, rid=0):
  rid = int(rid)
  try:	# Make sure report exist, of not redirect
    rep = Report.objects.get(id = rid)
  except Report.DoesNotExist:
    return HttpResponseRedirect(reverse('station_list'))

  signame = None
  sigtime = None
  if rep.signature:	# If report is signed don't updated database or show sign button
    form = None
    signame = rep.signature.username
    sigtime = rep.timestamp
  elif request.method == 'POST':
    form = ViewReportForm(rep=rep, data=request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      if request.user.check_password(cd['password']):
        rep.signature = request.user
        rep.timestamp = datetime.now()
        rep.save()
        return HttpResponseRedirect(reverse('report_list', args=[rep.station.id]))
      else:
        form.errors.password = "Felaktigt Lösenord"
  else:
    form = ViewReportForm(rep=rep)

  try:
    prev_rep = Report.objects.get(id = rep.previous)
  except Report.DoesNotExist:
    prev_rep = None

  if rep.is_complete():
    ft_list = Report.get_used_fuel_types(rep)
  else:
    ft_list = get_used_fuel_types(rep.station.id)
  page = list()

  rowh0 = [0, u"Avstämning mekaniska räkneverk"]
  rowh1 = [0, u"Avstämning elektroniska räkneverk"]
  rowh2 = [0, u"Inleveranser"]
  rowh3 = [0, u"Lageravstämmning idag"] 
  rowh4 = [0, u"Lagerdifferens från bokföringsårets början"]

  row00 = [1, u"", u""]
  row10 = [9, u"S:a mätarställning idag", "="]
  row11 = [9, u"Mätarställning föregående", "-"]
  row14 = [9, u"Sålda liter", "="]
  row15 = [9, u"Avläsning registerställning idag", "+"]
  row16 = [9, u"Registerställning föregående", "-"]
  row17 = [9, u"Sålda liter enligt elektr räkneverk", "="]
  row19 = [9, u"Differens idag", "="]
  row20 = [9, u"Differens föregående", "+"]
  row21 = [9, u"Ack differens", "="]
  row27 = [9, u"Summa inleveranser", "="]
  row28 = [9, u"Pejlat lager idag", ""]
  row29 = [9, u"Pejlat lager föregående", "+"]
  row32 = [9, u"Rundpumpning", "+"]
  row33 = [9, u"Teoretisk lager idag", "="]
  row34 = [9, u"Lagerdifferens idag", "="]
  row35 = [9, u"Ack lagerdifferens föregående", "="]
  row36 = [9, u"Ack lagerdifferens", "="]
  row37 = [9, u"Ack försäljning föregående", "+"]
  row39 = [9, u"Ack försäljning", "="]
  row40 = [9, u"Ack lagerdifferens", "%"]
  row41 = [9, u"Pumppris idag", ""]

  pumpnumlist = list()
  pumprowlist = list()
  pumpsolddict = dict()
  # Create a list with all pumps
  for pump in PumpStatus.objects.filter(report = rep):
    pump_num = pump.pump_nozle.pump.number
    if pump_num not in pumpnumlist:
      pumpnumlist.append(pump_num)
    pumpsolddict[(pump_num, pump.pump_nozle.fuel_type.id)] = pump.meter_reading
  pumpnumlist.sort()
  for pump_num in pumpnumlist:
    pumprowlist.append([9, u"Pump %d" % pump_num, "+"])

  # Find new pumps to create row 12
  newpumplist = list()
  newpumpdict = dict()
  for pump in Pump.objects.filter(station = rep.station, add_date = rep.date):
    newpumplist.append([9, u"Ing. mätarställning ny pump %d" % pump.number, "-"])
    for pumpnozle in PumpNozle.objects.filter(pump = pump):
      newpumpdict[(len(newpumplist), pumpnozle.fuel_type.id)] = pumpnozle.initial_meter_value

  # Find removed pumps to create row 13
  removedpumplist = list()
  removedpumpdict = dict()
  for pump in Pump.objects.filter(station = rep.station, removal_date = rep.date):
    removedpumplist.append([9, u"Utg. mätars. borttagen pump %s" % pump.number, "+"])
    for pumpnozle in PumpNozle.objects.filter(pump = pump):
      removedpumpdict[(len(removedpumplist), pumpnozle.fuel_type.id)] = pumpnozle.initial_meter_value

  # Create a list with all deliveries
  deliveryrowlist = list()
  totaldeliverydict = dict()
  for delivery in Delivery.objects.filter(report = rep):
    row = [9, u"Leverans", "+"]
    for ft_id, ft_name in ft_list:
      if delivery.fuel_type.id == ft_id:
        try:
          totaldeliverydict[ft_id] = totaldeliverydict[ft_id] + delivery.volume
        except:
          totaldeliverydict[ft_id] = delivery.volume
        row.append(delivery.volume)
      else:
        row.append("")
    deliveryrowlist.append(row)
 
  # Build the table one fuel typ at a time
  for ft_id,ft_name in ft_list:
    row00.append(ft_name)
    ftdo = FuelTypeData.objects.get(report = rep, fuel_type = ft_id)
    try:
      ftdo_prev = FuelTypeData.objects.get(report = prev_rep, fuel_type = ft_id)
    except:
      ftdo_prev = None

    for pumprow in pumprowlist:
      try:
        val = pumpsolddict[(pumprow[0], ft_id)]
        pumprow.append(val)
      except:
        pumprow.append("")
    row10.append(ftdo.mech_total_today)
    row14tot = ftdo.mech_total_today

    for i, pumprow in enumerate(newpumplist):
      try:
        val = newpumpdict[(i + 1, ft_id)]
        pumprow.append(val)
        row14tot = row14tot - val
      except:
        pumprow.append("")

    for i, pumprow in enumerate(removedpumplist):
      try:
        val = removedpumpdict[(i + 1, ft_id)]
        pumprow.append(val)
        row14tot = row14tot + val
      except:
        pumprow.append("")

    row17tot = ftdo.elec_meter_reading
    row21tot = 0.0
    row33tot = 0.0
    if prev_rep and ftdo_prev:
      row11.append(ftdo_prev.mech_total_today)
      row14.append(row14tot - ftdo_prev.mech_total_today)
      row16.append(ftdo_prev.elec_meter_reading)
      row17tot = row17tot - ftdo_prev.elec_meter_reading
      row20.append(ftdo_prev.accumulated_elec_diff)
      row21tot = row17tot - row14tot + ftdo_prev.accumulated_elec_diff
      row29.append(ftdo_prev.pin_meter_reading)
      row33tot = ftdo_prev.pin_meter_reading
    else:
      row11.append(u"None")
      row14.append(row14tot)
      row16.append(u"None")
      row20.append(u"None")
      row21tot = row17tot - row14tot
      row29.append(u"None")
    row15.append(ftdo.elec_meter_reading)
    row17.append(row17tot)
    row19.append(row17tot - row14tot)
    row21.append(row21tot)
    ftdo.accumulated_elec_diff = row21tot
    try:
      totdelivery = totaldeliverydict[ft_id]
    except KeyError:
      totdelivery = 0.0
    row27.append(totdelivery)
    row28.append(ftdo.pin_meter_reading)
    row32.append(ftdo.rundp_data)
    row33tot = row33tot + ftdo.rundp_data - row14tot + totdelivery
    row33.append(row33tot)
    row34.append(ftdo.pin_meter_reading - row33tot)
    if prev_rep and ftdo_prev:
      row35.append(ftdo_prev.accumulated_storage_diff)
      row36tot = ftdo.pin_meter_reading - row33tot + ftdo_prev.accumulated_storage_diff
      row36.append(row36tot)
      ftdo.accumulated_storage_diff = row36tot
      row37.append(ftdo_prev.accumulated_sold)
      row39.append(ftdo_prev.accumulated_sold + row14tot)
      ftdo.accumulated_sold = ftdo_prev.accumulated_sold + row14tot
      try:
        row40.append("%.3f" %(row36tot * 100 / (ftdo_prev.accumulated_sold + row14tot)))
      except ZeroDivisionError:
        row40.append("Inf")
    else:
      row35.append(u"None")
      row36.append(ftdo.pin_meter_reading - row33tot)
      ftdo.accumulated_storage_diff = ftdo.pin_meter_reading - row33tot
      row37.append(u"None")
      row39.append(row14tot)
      ftdo.accumulated_sold = row14tot
      try:
        row40.append("%.3f" % ((ftdo.pin_meter_reading - row33tot) * 100 / row14tot))
      except ZeroDivisionError:
        row40.append("Inf")
    row41.append(ftdo.pumpp_data)
    if form:	# Only save if the report isn't signed
      ftdo.save()

  # Add all rows to the page
  page.append(row00)
  page.append(rowh0)
  page += pumprowlist
  page.append(row10)
  page.append(row11)
  page += newpumplist
  page += removedpumplist
  page.append(row14)

  page.append(rowh1)
  page.append(row15)
  page.append(row16)
  page.append(row17)
  row18 = copy(row14)
  row18[2] = "-"
  page.append(row18)
  page.append(row19)
  page.append(row20)
  page.append(row21)

  page.append(rowh2)
  page += deliveryrowlist
  page.append(row27)

  page.append(rowh3)
  page.append(row28)
  page.append(row29)
  row30 = copy(row27)
  row30[2] = "+"
  page.append(row30)
  page.append(row18)	# row31 (row18 is row14 with a -)
  page.append(row32)
  page.append(row33)
  page.append(row34)

  page.append(rowh4)
  page.append(row35)
  page.append(row36)
  page.append(row37)
  row38 = copy(row14)
  row38[2] = "+"
  page.append(row38)
  page.append(row39)
  page.append(row40)
  page.append(row41)

  c = RequestContext(request, {'rep':rep, 'form':form, 'page':page,
                               'columns':len(ft_list) + 2,
                               'signame':signame, 'sigtime':sigtime})
  return render_to_response('pin/view_report.html', c)

