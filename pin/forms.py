from django import forms
from sbh.pin.models import GasStation, PumpNozle, Pump, FuelType, Delivery, PumpStatus, FuelTypeData

#def get_mechanical_meter_form(gid):
#    nozles = PumpNozle.objects.filter(pump__station=gid)
#    fields = dict()
#TODO handle GasStations with no pumps
#    for n in nozles:
#      fields["pn%d_%s" % (n.pump.number, n.fuel_type.id)] = forms.IntegerField()
    #raise ValueError
#    return type('MechanicalMeterForm', (forms.BaseForm,), { 'base_fields': fields })


class MechanicalMeterForm(forms.Form):

  def __init__(self, rep, *args, **kwargs):
    super(MechanicalMeterForm, self).__init__(*args, **kwargs)
    nozles = PumpNozle.objects.filter(pump__station=rep.station).order_by('id')
    for n in nozles:
      try:
        ps = PumpStatus.objects.get(report = rep, pump_nozle = n)
        self.fields['%d' % n.id] = forms.FloatField(label = u"Pump %d %s" % (n.pump.number, n.fuel_type.name), initial=ps.meter_reading)
      except:
        self.fields['%d' % n.id] = forms.FloatField(label = u"Pump %d %s" % (n.pump.number, n.fuel_type.name))

  def __unicode__(self):
    return self.fields

  def clean(self):
    cleaned_data = self.cleaned_data
    return cleaned_data


class DeliveryForm(forms.Form):

  def __init__(self, gs, *args, **kwargs):
    super(DeliveryForm, self).__init__(*args, **kwargs)

    fdict = gs.get_used_fuel_types()
    clist = list()
    for id,name in fdict:
      clist.append((id , name))

    self.fields['amount'] = forms.DecimalField(label = u"Mangd")
    self.fields['type'] = forms.ChoiceField(label = u"Typ", choices = clist)


class MiscForm(forms.Form):

  def __init__(self, rep, *args, **kwargs):
    super(MiscForm, self).__init__(*args, **kwargs)

    ft_list = GasStation.get_used_fuel_types(rep.station)

    for (ft_id, ft_name) in ft_list:
      try:
        ftdo = FuelTypeData.objects.get(report = rep, fuel_type = ft_id)
        self.fields['elec_%d' % ft_id] = forms.DecimalField(
                    label="Elektrisk matare %s" % ft_name,
                    initial=ftdo.elec_meter_reading)
        self.fields['pin_%d' % ft_id] = forms.DecimalField(
                    label="Pin matare %s" % ft_name,
                    initial=ftdo.pin_meter_reading)
        self.fields['rp_%d' % ft_id] = forms.DecimalField(
                    label="Rundpumpning %s" % ft_name,
                    initial=ftdo.rundp_data)
        self.fields['pp_%d' % ft_id] = forms.DecimalField(
                    label="Pumppris %s" % ft_name,
                    initial=ftdo.pumpp_data)
      except:
        self.fields['elec_%d' % ft_id] = forms.DecimalField(
                    label="Elektrisk matare %s" % ft_name)
        self.fields['pin_%d' % ft_id] = forms.DecimalField(
                    label="Pin matare %s" % ft_name)
        self.fields['rp_%d' % ft_id] = forms.DecimalField(
                    label="Rundpumpning %s" % ft_name)
        self.fields['pp_%d' % ft_id] = forms.DecimalField(
                    label="Pumppris %s" % ft_name)

class ViewReportForm(forms.Form):

  def __init__(self, rep, *args, **kwargs):
    super(ViewReportForm, self).__init__(*args, **kwargs)
    
    self.fields['password'] = forms.CharField(label=u'Password',
             widget=forms.PasswordInput(render_value=False))
