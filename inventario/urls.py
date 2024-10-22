from rest_framework import routers
from .views import InventarioViewSet
from django.urls import path, include



router = routers.DefaultRouter()


router.register(r'inventario', InventarioViewSet)


urlpatterns = [
    path ('', include(router.urls))
]