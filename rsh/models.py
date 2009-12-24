# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from sbh.main.models import GasStation

class Task(models.Model):
  name = models.CharField(max_length=100)
  station = models.ForeignKey(GasStation)
  time = models.TimeField('Time')
  periodstart = models.DateField('Date', null=True, blank=True)
  periodend = models.DateField('Date', null=True, blank=True)
  type = models.IntegerField()
  repeat = models.IntegerField(null=True, blank=True)
  dayofmonth = models.IntegerField(null=True, blank=True)
  days = models.CharField(max_length=32, null=True, blank=True)

  def __unicode__(self):
    return self.name

class DayTask(models.Model):
  name = models.CharField(max_length=100)
  station = models.ForeignKey(GasStation)
  time = models.TimeField('Time')
  date = models.DateField('Date')
  signature = models.ForeignKey(User, null=True, blank=True)
  timestamp = models.DateTimeField('Signature Time', null=True, blank=True)

  def __unicode__(self):
    return self.name
