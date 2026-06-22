from django.contrib import admin
from .models import Inspection, InspectionImage, Detection, Annotation, OperatorHeartbeat
admin.site.register([Inspection, InspectionImage, Detection, Annotation, OperatorHeartbeat])
