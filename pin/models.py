# coding: utf-8
from django.db import models
from django.contrib.auth.models import User
from sbh.main.models import GasStation

# Returns a list contaning all fuel types available at station order by name
def get_used_fuel_types(gid):
  result = list()
  # importing PumpNozle gives a circular reference
  all_nozles = PumpNozle.objects.filter(pump__station = gid).order_by('fuel_type__name')
  for nozle in all_nozles:
    val = (nozle.fuel_type.id, nozle.fuel_type.name)
    if val not in result:
      result.append(val)
  return result

class FuelType(models.Model):
  name = models.CharField(max_length=100)

  def __unicode__(self):
    return self.name

class Pump(models.Model):
  number = models.IntegerField()
  station = models.ForeignKey(GasStation)
  add_date = models.DateField()
  removal_date = models.DateField(null=True, blank=True)

  def __unicode__(self):
    return u"%d" % self.number

# Each pump can have multiple fuel types available
class PumpNozle(models.Model):
  pump = models.ForeignKey(Pump)
  fuel_type = models.ForeignKey(FuelType)
  initial_meter_value = models.FloatField()
  withdrawal_meter_value = models.FloatField(null=True, blank=True)

  def __unicode__(self):
    return u"Pump %d - %s" % (self.pump.number, self.fuel_type.name)

class Report(models.Model):
  date = models.DateField('Date')
  station = models.ForeignKey(GasStation)
  timestamp = models.DateTimeField('Signature Time', null=True)
  signature = models.ForeignKey(User, null=True)
  version = models.IntegerField(default=0)
  previous = models.IntegerField(unique=True, null=True) 

  # Returns a list contaning all fuel types available at the station order by name
  def get_used_fuel_types(self):
    result = list()
    all_nozles = FuelTypeData.objects.filter(report = self.id).order_by('fuel_type__name')
    for nozle in all_nozles:
      val = (nozle.fuel_type.id, nozle.fuel_type.name)
      if val not in result:
        result.append(val)
    return result

  def has_mech_data(self):
    return (len(PumpStatus.objects.filter(report = self.id)) != 0)

  def has_delivery_data(self):
    return (len(Delivery.objects.filter(report = self.id)) != 0)

  def has_fuel_type_data(self):
    if self.signature != None:
      return True
    for ft_id, ft_name in get_used_fuel_types(self.station):
      try:
        ftdo = FuelTypeData.objects.get(report = self, fuel_type = ft_id)
      except FuelTypeData.DoesNotExist:
        return False
      if ftdo.elec_meter_reading is None or ftdo.pin_meter_reading is None \
            or ftdo.rundp_data is None or ftdo.pumpp_data is None:
        return False
    return True

  def is_complete(self):
    try:
      return (self.has_mech_data() and self.has_fuel_type_data())
    except FuelTypeData.DoesNotExist:
      return False

class FuelTypeData(models.Model):
  report = models.ForeignKey(Report)
  fuel_type = models.ForeignKey(FuelType)
  mech_total_today = models.FloatField(null=True)		# row 10
  elec_meter_reading = models.FloatField(null=True)		# row 15
  accumulated_elec_diff = models.FloatField(null=True)		# row 21
  pin_meter_reading = models.FloatField(null=True)		# row 28
  rundp_data = models.FloatField(null=True)			# row 32
  accumulated_storage_diff = models.FloatField(null=True)	# row 36
  accumulated_sold = models.FloatField(null=True)		# row 39
  pumpp_data = models.FloatField(null=True)			# row 41

class PumpStatus(models.Model):
  report = models.ForeignKey(Report)
  pump_nozle = models.ForeignKey(PumpNozle)
  meter_reading = models.FloatField()

class Delivery(models.Model):
  report = models.ForeignKey(Report)
  fuel_type = models.ForeignKey(FuelType)
  station = models.ForeignKey(GasStation)
  volume = models.FloatField()

  def __unicode__(self):
    return self.fuel_type.name
