from rest_framework import routers
from .views import FichaTecViewSet
from django.urls import path, include

router = routers.DefaultRouter()


router.register(r'ficha_tecnica', FichaTecViewSet)


urlpatterns = [
    path('', include (router.urls))
]