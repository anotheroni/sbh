# coding: utf-8
from sbh.pin.models import FuelType, Pump, PumpNozle
from sbh.main.models import GasStation
from django.contrib import admin

#class GasStationForm(forms.ModelForm):

#  def __init__(self, *args, **kwargs):
#    super(GasStationForm, self).__init__(*args, **kwargs)

class PumpInline(admin.TabularInline):
  model = Pump
  fk_name = 'station'

class GasStationAdmin(admin.ModelAdmin):
  inlines = [
    PumpInline
  ]

class PumpNozleInline(admin.TabularInline):
  model = PumpNozle
  fk_name = 'pump'

class PumpAdmin(admin.ModelAdmin):
  inlines = [
    PumpNozleInline
  ]
    

admin.site.register(GasStation, GasStationAdmin)
admin.site.register(FuelType)
admin.site.register(Pump, PumpAdmin)
