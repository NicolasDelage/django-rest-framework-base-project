from django.urls import path, include
from rest_framework.routers import DefaultRouter

from heroad import views


router = DefaultRouter()
router.register('address', views.AddressViewSet)
router.register('vehicle', views.VehicleViewSet)
app_name = 'heroad'

urlpatterns = [
    path('', include(router.urls))
]