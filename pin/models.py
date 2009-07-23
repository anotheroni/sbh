from django.db import models

# Create your models here.

class GasStation(models.Model):
  name = models.CharField(max_length=100)
  address = models.CharField(max_length=100)
  phone = models.CharField(max_length=30)
  company = models.CharField(max_length=100)

  def __unicode__(self):
    return self.name

  # Returns a list contaning all fuel types available at the station order by name
  def get_used_fuel_types(self):
    result = list()
    all_nozles = PumpNozle.objects.filter(pump__station = self.id).order_by('fuel_type__name')
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
  initial_meter_value = models.FloatField()
  withdrawal_meter_value = models.FloatField()
  station = models.ForeignKey(GasStation)

  def __unicode__(self):
    return self.number

# Each pump can have multiple fuel types available
class PumpNozle(models.Model):
  pump = models.ForeignKey(Pump)
  fuel_type = models.ForeignKey(FuelType)

  def __unicode__(self):
    return "Pump %d - %s" % (self.pump.number, self.fuel_type.name)

class Report(models.Model):
  date = models.DateField('Date')
  station = models.ForeignKey(GasStation)
  signature = models.DateTimeField('Signature Time', blank=True)
  version = models.IntegerField(default=0)
  previous = models.IntegerField(unique=True, blank=True) 

  def has_mech_data(self):
    return (len(PumpStatus.objects.filter(report = self.id)) != 0)

  def has_delivery_data(self):
    return (len(Delivery.objects.filter(report = self.id)) != 0)

  def has_fuel_type_data(self):
    return (len(FuelTypeData.objects.filter(report = self.id)) != 0)

  def is_complete(self):
    return (self.has_mech_data() and self.has_fuel_type_data())

class FuelTypeData(models.Model):
  report = models.ForeignKey(Report)
  fuel_type = models.ForeignKey(FuelType)
  mech_total_today = models.FloatField(blank=True)		# row 10
  elec_meter_reading = models.FloatField(blank=True)		# row 15
  accumulated_elec_diff = models.FloatField(blank=True)		# row 21
  pin_meter_reading = models.FloatField(blank=True)		# row 28
  rundp_data = models.FloatField(blank=True)			# row 32
  accumulated_storage_diff = models.FloatField(blank=True)	# row 36
  accumulated_sold = models.FloatField(blank=True)		# row 39
  pumpp_data = models.FloatField(blank=True)			# row 41

class PumpStatus(models.Model):
  report = models.ForeignKey(Report)
  pump_nozle = models.ForeignKey(PumpNozle)
  meter_reading = models.FloatField()

class Delivery(models.Model):
  report = models.ForeignKey(Report)
  fuel_type = models.ForeignKey(FuelType)
  station = models.ForeignKey(GasStation)
  volume = models.FloatField()
