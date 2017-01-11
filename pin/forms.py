# coding: utf-8
from django import forms
from django.forms.forms import BoundField
from django.utils.safestring import mark_safe
from sbh.pin.models import GasStation, PumpNozle, Pump, FuelType, Delivery, PumpStatus, FuelTypeData, get_used_fuel_types

#def get_mechanical_meter_form(gid):
#    nozles = PumpNozle.objects.filter(pump__station=gid)
#    fields = dict()
#TODO handle GasStations with no pumps
#    for n in nozles:
#      fields["pn%d_%s" % (n.pump.number, n.fuel_type.id)] = forms.IntegerField()
    #raise ValueError
#    return type('MechanicalMeterForm', (forms.BaseForm,), { 'base_fields': fields })


class MechanicalMeterForm(forms.Form):

  station = None

  def __init__(self, rep, *args, **kwargs):
    super(MechanicalMeterForm, self).__init__(*args, **kwargs)
    self.station = rep.station
    nozles = PumpNozle.objects.filter(pump__station=rep.station).order_by('id')
    for n in nozles:
      try:
        ps = PumpStatus.objects.get(report = rep, pump_nozle = n)
        self.fields['%d_%d' % (n.pump.id, n.fuel_type.id)] = forms.FloatField(label = u"Pump %d %s" % (n.pump.number, n.fuel_type.name), initial=ps.meter_reading)
      except PumpStatus.DoesNotExist:   # No initial value
        self.fields['%d_%d' % (n.pump.id, n.fuel_type.id)] = forms.FloatField(label = u"Pump %d %s" % (n.pump.number, n.fuel_type.name))

  def __unicode__(self):
    return self.fields

#  def clean(self):
#    cleaned_data = self.cleaned_data
#    return cleaned_data
  def as_spsh(self):
    if self.station is None:
      return mark_safe(u"No pumps")
    fuel_type_list = get_used_fuel_types(self.station.id)
    output, hidden_fields = [], []

    # Top row / Header
    output.append(u"<tr><th>&nbsp;</th>")   # Top left is empty
    for ft_id, name in fuel_type_list:
      output.append(u"<th>%s</th>" % name)
    output.append(u"</tr>")

    # Add table rows, one for each pump
    for pump in Pump.objects.filter(station=self.station).order_by('number'):
      output.append(u"<tr><th>Pump %d</th>" % pump.number)
      for ft_id, ft_name in fuel_type_list:
        try:
          name = "%d_%d" % (pump.id, ft_id)
          bf = BoundField(self, self.fields[name], name)
          #bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
          if bf.errors:
            output.append(u"<td class=\"table_error\">%s</td>" % unicode(bf))
          else:
            output.append(u"<td>%s</td>" % unicode(bf))
        except: #KeyError:
          output.append(u"<td>&nbsp;</td>")

    return mark_safe(u'\n'.join(output))

class DeliveryForm(forms.Form):

  def __init__(self, gs, *args, **kwargs):
    super(DeliveryForm, self).__init__(*args, **kwargs)

    fdict = get_used_fuel_types(gs.id)
    clist = list()
    for id,name in fdict:
      clist.append((id , name))

    self.fields['amount'] = forms.DecimalField(label = u"Mängd")
    self.fields['type'] = forms.ChoiceField(label = u"Typ", choices = clist)


class MiscForm(forms.Form):
  
  station = None
  misc_fields = [('elec', u'Elektrisk mätare', 'elec_meter_reading'),
                 ('pin', u'Pin mätare', 'pin_meter_reading'),
                 ('rp', u'Rundpumpning', 'rundp_data'),
                 ('pp', u'Pumppris', 'pumpp_data')]

  def __init__(self, rep, *args, **kwargs):
    super(MiscForm, self).__init__(*args, **kwargs)
    self.station = rep.station

    ft_list = get_used_fuel_types(rep.station.id)

    for (ft_id, ft_name) in ft_list:
      try:
        ftdo = FuelTypeData.objects.get(report = rep, fuel_type = ft_id)
        for mf_id, mf_label, mf_attr in self.misc_fields:
          self.fields['%s_%d' % (mf_id, ft_id)] = forms.DecimalField(
                    label="%s %s" % (mf_label, ft_name),
                    initial=ftdo.__dict__[mf_attr])
      except:
        for mf_id, mf_label, mf_attr in self.misc_fields:
          self.fields['%s_%d' % (mf_id, ft_id)] = forms.DecimalField(
                    label="%s %s" % (mf_label, ft_name))

  def as_spsh(self):
    if self.station is None:
      return mark_safe(u"No Fuel Types")
    fuel_type_list = get_used_fuel_types(self.station.id)
    output, hidden_fields = [], []

    # Top row / Header
    output.append(u"<tr><th>&nbsp;</th>")   # Top left is empty
    for ft_id, name in fuel_type_list:
      output.append(u"<th>%s</th>" % name)
    output.append(u"</tr>")

    # Add table rows
    for mf_id, mf_label, mf_attr in self.misc_fields:
      output.append(u"<tr><th>%s</th>" % mf_label)
      for ft_id, ft_name in fuel_type_list:
        try:
          name = "%s_%d" % (mf_id, ft_id)
          bf = BoundField(self, self.fields[name], name)
          #bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
          if bf.errors:
            output.append(u"<td class=\"table_error\">%s</td>" % unicode(bf))
          else:
            output.append(u"<td>%s</td>" % unicode(bf))
        except: #KeyError:
          output.append(u"<td>&nbsp;</td>")

    return mark_safe(u'\n'.join(output))

class ViewReportForm(forms.Form):

  def __init__(self, rep, *args, **kwargs):
    super(ViewReportForm, self).__init__(*args, **kwargs)
    
    self.fields['password'] = forms.CharField(label=u'Password',
             widget=forms.PasswordInput(render_value=False))
