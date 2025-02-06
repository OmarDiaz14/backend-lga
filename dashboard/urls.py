from rest_framework import routers
from .views import DashboardViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'dashboard', DashboardViewSet)

urlpatterns = [
    path ('', include(router.urls))
]