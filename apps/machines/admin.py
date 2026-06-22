from django.contrib import admin
from .models import Machine, Camera, Laser, DeviceEvent
admin.site.register([Machine, Camera, Laser, DeviceEvent])
