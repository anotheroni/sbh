# coding: utf-8
from django import forms
from django.forms.forms import BoundField
from django.utils.safestring import mark_safe
from sbh.rsh.models import Task, DayTask
from django.forms.extras.widgets import SelectDateWidget

def _choosen(value):
  if value == '0':
    return None
  else:
    return '1'

class NewTaskForm(forms.Form):

  taskTypes = [(1,"Dag"), (2,"Vecka"), (3,"Månad")]
  taskHour = [(0,"00:00"), (1,"01:00"), (2,"02:00"), (3,"03:00"), (4,"04:00"),
              (5,"05:00"), (6,"06:00"), (7,"07:00"), (8,"08:00"), (9,"09:00"),
              (10,"10:00"), (11,"11:00"), (12,"12:00"), (13,"13:00"), (14,"14:00"),
              (15,"15:00"), (16,"16:00"), (17,"17:00"), (18,"18:00"), (19,"19:00"),
              (20,"20:00"), (21,"21:00"), (22,"22:00"), (23,"23:00")]

  def __init__(self, gid, tid=0, *args, **kwargs):
    super(NewTaskForm, self).__init__(*args, **kwargs)

    task = None
    if tid != 0:
      try:
        task = Task.objects.get(id = tid)
      except Task.DoesNotExist:
        pass

    if task:
      self.fields['name'] = forms.CharField(label=u"Aktivitet", initial=task.name)
      self.fields['time'] = forms.ChoiceField(label=u"Tid", choices = self.taskHour,
                                            initial=task.time.hour)
      self.fields['periodstart'] = forms.DateField(label=u"Period Början", required=False,
                                            initial=task.periodstart,
                                            widget=SelectDateWidget())
      self.fields['periodend'] = forms.DateField(label=u"Period Slut", required=False,
                                            initial=task.periodend,
                                            widget=SelectDateWidget())
      self.fields['type'] = forms.ChoiceField(label=u"Typ", choices = self.taskTypes,
                                            widget=forms.RadioSelect(),
                                            initial=task.type)
      self.fields['dayofmonth'] = forms.IntegerField(label=u"Dag i månad", required=False,
                                min_value=1, max_value=31, initial=task.dayofmonth)
      self.fields['repeat'] = forms.IntegerField(label=u"Upprepa var", required=False,
                            min_value=0, initial=task.repeat)
    else:
      self.fields['name'] = forms.CharField(label=u"Aktivitet")
      self.fields['time'] = forms.ChoiceField(label=u"Tid", choices = self.taskHour)
      self.fields['periodstart'] = forms.DateField(label=u"Period Början", required=False,
                                                 widget=SelectDateWidget())
      self.fields['periodend'] = forms.DateField(label=u"Period Slut", required=False,
                                                 widget=SelectDateWidget())
      self.fields['type'] = forms.ChoiceField(label=u"Typ", choices = self.taskTypes,
                                                 widget=forms.RadioSelect())
      self.fields['dayofmonth'] = forms.IntegerField(label=u"Dag i månad", required=False,
                                min_value=1, max_value=31)
      self.fields['repeat'] = forms.IntegerField(label=u"Återupprepning", required=False,
                            min_value=0)

    if task and task.type == 2:
      self.fields['daymon'] = forms.BooleanField(label=u"Måndag", required=False,
                                            initial=_choosen(task.days[0]))
      self.fields['daytue'] = forms.BooleanField(label=u"Tisdag", required=False,
                                            initial=_choosen(task.days[1]))
      self.fields['daywed'] = forms.BooleanField(label=u"Onsdag", required=False,
                                            initial=_choosen(task.days[2]))
      self.fields['daythr'] = forms.BooleanField(label=u"Torsdag", required=False,
                                            initial=_choosen(task.days[3]))
      self.fields['dayfri'] = forms.BooleanField(label=u"Fredag", required=False,
                                            initial=_choosen(task.days[4]))
      self.fields['daysat'] = forms.BooleanField(label=u"Lördag", required=False,
                                            initial=_choosen(task.days[5]))
      self.fields['daysun'] = forms.BooleanField(label=u"Söndag", required=False,
                                            initial=_choosen(task.days[6]))
    else:
      self.fields['daymon'] = forms.BooleanField(label=u"Måndag", required=False)
      self.fields['daytue'] = forms.BooleanField(label=u"Tisdag", required=False)
      self.fields['daywed'] = forms.BooleanField(label=u"Onsdag", required=False)
      self.fields['daythr'] = forms.BooleanField(label=u"Torsdag", required=False)
      self.fields['dayfri'] = forms.BooleanField(label=u"Fredag", required=False)
      self.fields['daysat'] = forms.BooleanField(label=u"Lördag", required=False)
      self.fields['daysun'] = forms.BooleanField(label=u"Söndag", required=False)

