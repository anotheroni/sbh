# coding: utf-8
from django import forms
from django.forms.forms import BoundField
from django.utils.safestring import mark_safe
from sbh.rsh.models import Event, DayEvent

class NewEventForm(forms.Form):

  eventTypes = [(1,"Dag"), (2,"Vecka"), (3,"Månad")]

  def __init__(self, tid=0, *args, **kwargs):
    super(NewEventForm, self).__init__(*args, **kwargs)

    event = None
    if tid != 0:
      try:
        event = Event.objects.get(id = tid)
      except Event.DoesNotExist:
        pass

    if event:
      self.fields['name'] = forms.CharField(label=u"Aktivitet", initial=event.name)
      self.fields['time'] = forms.TimeField(input_formats='%H', label=u"Tid",
                                            initial=event.time)
      self.fields['periodstart'] = forms.DateField(label=u"Period Början",
                                            initial=event.periodstart)
      self.fields['periodend'] = forms.DateField(label=u"Period Slut",
                                            initial=event.periodend)
# TODO initial
      self.fields['eventtype'] = forms.ChoiceField(choices = self.eventTypes)
      self.fields['daymon'] = forms.BooleanField(label=u"Måndag", initial=event.mon)
      self.fields['daytue'] = forms.BooleanField(label=u"Tisdag", initial=event.tue)
      self.fields['daywed'] = forms.BooleanField(label=u"Onsdag", initial=event.wed)
      self.fields['daythr'] = forms.BooleanField(label=u"Torsdag", initial=event.thr)
      self.fields['dayfri'] = forms.BooleanField(label=u"Fredag", initial=event.fri)
      self.fields['daysat'] = forms.BooleanField(label=u"Lördag", initial=event.sat)
      self.fields['daysun'] = forms.BooleanField(label=u"Söndag", initial=event.sun)
      self.fields['dayofmonth'] = forms.IntegerField(label=u"Dag i månaden",
                                min_value=1, max_value=31, initial=event.dayofmonth)
      self.fields['repeat'] = forms.IntegerField(label=u"Återupprepning",
                            min_value=0, initial=event.repeat)
    else:
      self.fields['name'] = forms.CharField(label=u"Aktivitet")
      self.fields['time'] = forms.TimeField(input_formats='%H', label=u"Tid")
      self.fields['periodstart'] = forms.DateField(label=u"Period Början")
      self.fields['periodend'] = forms.DateField(label=u"Period Slut")
      self.fields['eventtype'] = forms.ChoiceField(choices = self.eventTypes)
      self.fields['daymon'] = forms.BooleanField(label=u"Måndag")
      self.fields['daytue'] = forms.BooleanField(label=u"Tisdag")
      self.fields['daywed'] = forms.BooleanField(label=u"Onsdag")
      self.fields['daythr'] = forms.BooleanField(label=u"Torsdag")
      self.fields['dayfri'] = forms.BooleanField(label=u"Fredag")
      self.fields['daysat'] = forms.BooleanField(label=u"Lördag")
      self.fields['daysun'] = forms.BooleanField(label=u"Söndag")
      self.fields['dayofmonth'] = forms.IntegerField(label=u"Dag i månaden",
                                min_value=1, max_value=31)
      self.fields['repeat'] = forms.IntegerField(label=u"Återupprepning",
                            min_value=0)
