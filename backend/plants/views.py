from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Plant, PlantingCycle, Event, Task
from .serializers import (
    PlantSerializer,
    PlantListSerializer,
    PlantingCycleSerializer,
    EventSerializer,
    TaskSerializer
)


class PlantViewSet(viewsets.ModelViewSet):
    """ViewSet für Pflanzen"""
    queryset = Plant.objects.all().prefetch_related('cycles', 'cycles__events', 'cycles__tasks')
    serializer_class = PlantSerializer

    def get_serializer_class(self):
        """Verwende vereinfachten Serializer für list"""
        if self.action == 'list':
            return PlantListSerializer
        return PlantSerializer

    def get_queryset(self):
        """Filter für Pflanzen"""
        queryset = super().get_queryset()

        # Suche
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(variety__icontains=search) |
                Q(seed_source__icontains=search)
            )

        # Filter nach Jahr
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(cycles__year=year).distinct()

        return queryset.annotate(cycle_count=Count('cycles'))

    @action(detail=True, methods=['get'])
    def cycles_detail(self, request, pk=None):
        """Detaillierte Zyklus-Informationen für eine Pflanze"""
        plant = self.get_object()
        cycles = plant.cycles.all()
        serializer = PlantingCycleSerializer(cycles, many=True)
        return Response(serializer.data)


class PlantingCycleViewSet(viewsets.ModelViewSet):
    """ViewSet für Anbau-Zyklen"""
    queryset = PlantingCycle.objects.all().select_related('plant').prefetch_related('events', 'tasks')
    serializer_class = PlantingCycleSerializer

    def get_queryset(self):
        """Filter für Anbau-Zyklen"""
        queryset = super().get_queryset()

        # Filter nach Jahr
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(year=year)

        # Filter nach Status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # Filter nach Pflanze
        plant = self.request.query_params.get('plant', None)
        if plant:
            queryset = queryset.filter(plant_id=plant)

        return queryset

    @action(detail=True, methods=['post'])
    def add_event(self, request, pk=None):
        """Event zu einem Zyklus hinzufügen"""
        cycle = self.get_object()
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(planting_cycle=cycle)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        """Task zu einem Zyklus hinzufügen"""
        cycle = self.get_object()
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(planting_cycle=cycle)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet für Events"""
    queryset = Event.objects.all().select_related('planting_cycle', 'planting_cycle__plant')
    serializer_class = EventSerializer

    def get_queryset(self):
        """Filter für Events"""
        queryset = super().get_queryset()

        # Filter nach Zyklus
        cycle = self.request.query_params.get('cycle', None)
        if cycle:
            queryset = queryset.filter(planting_cycle_id=cycle)

        # Filter nach Event-Typ
        event_type = self.request.query_params.get('type', None)
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filter nach Datum
        date_from = self.request.query_params.get('date_from', None)
        if date_from:
            queryset = queryset.filter(event_date__gte=date_from)

        date_to = self.request.query_params.get('date_to', None)
        if date_to:
            queryset = queryset.filter(event_date__lte=date_to)

        return queryset


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet für Tasks"""
    queryset = Task.objects.all().select_related('planting_cycle', 'planting_cycle__plant')
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Filter für Tasks"""
        queryset = super().get_queryset()

        # Filter nach completed Status
        completed = self.request.query_params.get('completed', None)
        if completed is not None:
            completed_bool = completed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(completed=completed_bool)

        # Filter nach Zyklus
        cycle = self.request.query_params.get('cycle', None)
        if cycle:
            queryset = queryset.filter(planting_cycle_id=cycle)

        # Filter nach Priorität
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)

        # Nur überfällige Tasks
        overdue = self.request.query_params.get('overdue', None)
        if overdue and overdue.lower() in ['true', '1', 'yes']:
            today = timezone.now().date()
            queryset = queryset.filter(
                completed=False,
                due_date__lt=today
            )

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        """Toggle completed Status"""
        task = self.get_object()
        task.completed = not task.completed
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class DashboardViewSet(viewsets.ViewSet):
    """Dashboard mit aggregierten Daten"""

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Dashboard-Statistiken"""
        current_year = timezone.now().year
        today = timezone.now().date()

        # Aktuelle Zyklen
        current_cycles = PlantingCycle.objects.filter(
            year=current_year
        ).exclude(status='finished')

        # Aufgaben
        open_tasks = Task.objects.filter(completed=False)
        overdue_tasks = open_tasks.filter(due_date__lt=today)
        upcoming_tasks = open_tasks.filter(
            due_date__gte=today,
            due_date__lte=today + timedelta(days=7)
        )

        # Ereignisse der letzten 30 Tage
        recent_events = Event.objects.filter(
            event_date__gte=today - timedelta(days=30)
        )

        # Ernten der letzten 30 Tage
        recent_harvests = Event.objects.filter(
            event_type='harvest',
            event_date__gte=today - timedelta(days=30)
        ).aggregate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        )

        data = {
            'current_year': current_year,
            'stats': {
                'total_plants': Plant.objects.count(),
                'current_cycles': current_cycles.count(),
                'open_tasks': open_tasks.count(),
                'overdue_tasks': overdue_tasks.count(),
                'recent_events': recent_events.count(),
            },
            'cycles': PlantingCycleSerializer(
                current_cycles[:10],
                many=True
            ).data,
            'upcoming_tasks': TaskSerializer(
                upcoming_tasks[:10],
                many=True
            ).data,
            'overdue_tasks': TaskSerializer(
                overdue_tasks[:10],
                many=True
            ).data,
            'recent_harvests': {
                'count': recent_harvests['count'] or 0,
                'total_quantity': float(recent_harvests['total_quantity'] or 0)
            }
        }

        return Response(data)
