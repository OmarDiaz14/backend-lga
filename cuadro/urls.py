from rest_framework import routers
from .views import SeccionViewSet, SerieViewSet, SubSerieViewSet, ImportExcelView
from django.urls import path, include

router = routers.DefaultRouter()

router.register(r'seccion', SeccionViewSet )
router.register(r'serie', SerieViewSet)
router.register(r'subserie', SubSerieViewSet)
router.register(r'import',ImportExcelView, basename='import')

urlpatterns = [
    path('', include (router.urls)),
]

