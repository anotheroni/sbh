# coding: utf-8
from django.db import models
from django.contrib.auth.models import User


class GasStation(models.Model):
  name = models.CharField(max_length=100)
  address = models.CharField(max_length=100)
  phone = models.CharField(max_length=30)
  company = models.CharField(max_length=100)

  def __unicode__(self):
    return self.name


# Class granting user rights to gasstations
class UserAuth(models.Model):
  user = models.ForeignKey(User)
  station = models.ForeignKey(GasStation)
  level = models.IntegerField(default=0)
  app = models.IntegerField()

  def __unicode__(self):
    return u"%s - %s - %d" % (self.user.username, self.station.name, self.app)

