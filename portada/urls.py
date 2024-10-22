from rest_framework import routers
from .views import PortadaViewSet
from django.urls import path, include



router = routers.DefaultRouter()


router.register(r'portada', PortadaViewSet)


urlpatterns = [
    path ('', include(router.urls))
]