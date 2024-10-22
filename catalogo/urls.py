from rest_framework import routers
from .views import CatalogoViewSet, DestinoViewSet, TypeViewSet, ValorViewSet
from django.urls import path, include

router = routers.DefaultRouter()

router.register(r'Catalogo', CatalogoViewSet)
router.register(r'Destino', DestinoViewSet)
router.register(r'Type', TypeViewSet)
router.register(r'Valores', ValorViewSet)

urlpatterns = [
    path('', include (router.urls)),
]