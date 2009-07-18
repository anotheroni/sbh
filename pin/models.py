from django.db import models

# Create your models here.

class GasStation(models.Model):
  name = models.CharField(max_length=100)
  address = models.CharField(max_length=100)
  phone = models.CharField(max_length=30)
  company = models.CharField(max_length=100)

  def __unicode__(self):
    return self.name

  # Returns a dictionary contaning all fuel types available at the station
  def get_used_fuel_types(self):
    result = dict()
    all_nozles = PumpNozle.objects.filter(pump__station = self.id)
    for nozle in all_nozles:
      result[nozle.fuel_type.id] = nozle.fuel_type.name
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

  def has_mech_data(self):
    return (len(PumpStatus.objects.filter(report = self.id)) != 0)

  def has_delivery_data(self):
    return (len(Delivery.objects.filter(report = self.id)) != 0)

  def has_acc_data(self):
    return (len(AccumulatedData.objects.filter(report = self.id)) != 0)

  def has_pin_data(self):
    return (len(PinMeter.objects.filter(report = self.id)) != 0)

  def has_elec_data(self):
    return (len(ElectronicMeterCounter.objects.filter(report = self.id)) != 0)

  def is_complete(self):
    return (self.has_mech_data() and self.has_acc_data() and self.has_pin_data() and self.has_elec_data())

class AccumulatedData(models.Model):
  report = models.ForeignKey(Report)
  fuel_type = models.ForeignKey(FuelType)
  accumulated_storage_diff = models.FloatField()
  accumulated_sold = models.FloatField()

class ElectronicMeterCounter(models.Model):
  report = models.ForeignKey(Report)
  meter_reading = models.FloatField()
  accumulated_diff = models.FloatField()
  fuel_type = models.ForeignKey(FuelType)

class PinMeter(models.Model):
  report = models.ForeignKey(Report)
  meter_reading = models.FloatField()
  fuel_type = models.ForeignKey(FuelType)

class PumpStatus(models.Model):
  report = models.ForeignKey(Report)
  pump_nozle = models.ForeignKey(PumpNozle)
  meter_reading = models.FloatField()

class Delivery(models.Model):
  report = models.ForeignKey(Report)
  fuel_type = models.ForeignKey(FuelType)
  station = models.ForeignKey(GasStation)
  volume = models.FloatField()
