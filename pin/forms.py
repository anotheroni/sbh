from django import forms
from sbh.pin.models import GasStation, PumpNozle, Pump, FuelType, Delivery

#def get_mechanical_meter_form(gid):
#    nozles = PumpNozle.objects.filter(pump__station=gid)
#    fields = dict()
#TODO handle GasStations with no pumps
#    for n in nozles:
#      fields["pn%d_%s" % (n.pump.number, n.fuel_type.id)] = forms.IntegerField()
    #raise ValueError
#    return type('MechanicalMeterForm', (forms.BaseForm,), { 'base_fields': fields })


class MechanicalMeterForm(forms.Form):

  def __init__(self, gid, *args, **kwargs):
    super(MechanicalMeterForm, self).__init__(*args, **kwargs)
    nozles = PumpNozle.objects.filter(pump__station=gid).order_by('id')
    for n in nozles:
      self.fields['%d' % n.id] = forms.IntegerField(label = "pn%d_tp%s" % (n.pump.number, n.fuel_type.id))

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
    for id in fdict:
      clist.append((id , fdict[id]))

    self.fields['amount'] = forms.DecimalField(label = "Mangd")
    self.fields['type'] = forms.ChoiceField(label = "Typ", choices = clist)


class MiscForm(forms.Form):

  def __init__(self, gid, *args, **kwargs):
    super(MiscForm, self).__init__(*args, **kwargs)

    nozles = PumpNozle.objects.filter(pump__station=gid)
