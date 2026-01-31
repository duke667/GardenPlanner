from rest_framework import serializers
from .models import Plant, PlantingCycle, Event, Task


class EventSerializer(serializers.ModelSerializer):
    """Serializer für Events"""
    event_type_display = serializers.CharField(
        source='get_event_type_display',
        read_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id',
            'planting_cycle',
            'event_type',
            'event_type_display',
            'event_date',
            'location',
            'quantity',
            'notes',
            'created_at'
        ]
        read_only_fields = ['created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer für Tasks"""
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'planting_cycle',
            'title',
            'description',
            'due_date',
            'completed',
            'completed_at',
            'priority',
            'priority_display',
            'created_at'
        ]
        read_only_fields = ['created_at', 'completed_at']


class PlantingCycleSerializer(serializers.ModelSerializer):
    """Serializer für PlantingCycles"""
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    plant_variety = serializers.CharField(source='plant.variety', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    events = EventSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    event_count = serializers.IntegerField(
        source='events.count',
        read_only=True
    )
    task_count = serializers.IntegerField(
        source='tasks.count',
        read_only=True
    )

    class Meta:
        model = PlantingCycle
        fields = [
            'id',
            'plant',
            'plant_name',
            'plant_variety',
            'year',
            'status',
            'status_display',
            'seed_saved',
            'seed_saved_notes',
            'events',
            'tasks',
            'event_count',
            'task_count',
            'created_at'
        ]
        read_only_fields = ['created_at']


class PlantSerializer(serializers.ModelSerializer):
    """Serializer für Plants"""
    cycles = PlantingCycleSerializer(many=True, read_only=True)
    cycle_count = serializers.IntegerField(
        source='cycles.count',
        read_only=True
    )
    latest_cycle = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'variety',
            'seed_source',
            'notes',
            'cycles',
            'cycle_count',
            'latest_cycle',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_latest_cycle(self, obj):
        """Gibt den neuesten Zyklus zurück"""
        latest = obj.cycles.order_by('-year').first()
        if latest:
            return PlantingCycleSerializer(latest).data
        return None


class PlantListSerializer(serializers.ModelSerializer):
    """Vereinfachter Serializer für Pflanzenliste"""
    cycle_count = serializers.IntegerField(
        source='cycles.count',
        read_only=True
    )
    latest_cycle_year = serializers.SerializerMethodField()
    latest_cycle_status = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'variety',
            'cycle_count',
            'latest_cycle_year',
            'latest_cycle_status',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_latest_cycle_year(self, obj):
        latest = obj.cycles.order_by('-year').first()
        return latest.year if latest else None

    def get_latest_cycle_status(self, obj):
        latest = obj.cycles.order_by('-year').first()
        return latest.get_status_display() if latest else None
