# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from sbh.pin.models import GasStation

class Event(models.Model):
  name = models.CharField(max_length=100)
  station = models.ForeignKey(GasStation)
  time = models.TimeField('Time')
  periodstart = models.DateField('Date')
  periodend = models.DateField('Date')
  repeat = models.IntegerField()
  dayofmonth = models.IntegerField()
  mon = models.BooleanField()
  tue = models.BooleanField()
  wed = models.BooleanField()
  thr = models.BooleanField()
  fri = models.BooleanField()
  sat = models.BooleanField()
  sun = models.BooleanField()

  def __unicode__(self):
    return self.name

class DayEvent(models.Model):
  name = models.CharField(max_length=100)
  station = models.ForeignKey(GasStation)
  date = models.DateField('Date')
  signature = models.ForeignKey(User, null=True)
  timestamp = models.DateTimeField('Signature Time', null=True)

  def __unicode__(self):
    return self.name
