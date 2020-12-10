from django.urls import path, include
from rest_framework.routers import DefaultRouter

from heroad import views


router = DefaultRouter()
router.register('address', views.AddressViewSet)
router.register('vehicle', views.VehicleViewSet)
router.register('patient', views.PatientViewSet)
router.register('run', views.RunViewSet)
router.register('master_run', views.MasterRunViewSet, basename='master_run')
app_name = 'heroad'

urlpatterns = [
    path('', include(router.urls))
]
