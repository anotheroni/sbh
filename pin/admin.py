from sbh.pin.models import GasStation, FuelType, Pump, PumpNozle
from django.contrib import admin

#class GasStationForm(forms.ModelForm):

#  def __init__(self, *args, **kwargs):
#    super(GasStationForm, self).__init__(*args, **kwargs)

    

#class GasStationAdmin(admin.ModelAdmin):
#  form = GasStationForm

#admin.site.register(GasStationAdmin)
admin.site.register(GasStation)
admin.site.register(FuelType)
admin.site.register(Pump)
admin.site.register(PumpNozle)
