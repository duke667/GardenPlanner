from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlantViewSet,
    PlantingCycleViewSet,
    EventViewSet,
    TaskViewSet,
    DashboardViewSet
)

router = DefaultRouter()
router.register(r'plants', PlantViewSet, basename='plant')
router.register(r'cycles', PlantingCycleViewSet, basename='plantingcycle')
router.register(r'events', EventViewSet, basename='event')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
