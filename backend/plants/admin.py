from django.contrib import admin
from .models import Plant, PlantingCycle, Event, Task


class PlantingCycleInline(admin.TabularInline):
    """Inline für Anbau-Zyklen in der Pflanzen-Ansicht"""
    model = PlantingCycle
    extra = 0
    fields = ['year', 'status', 'seed_saved']
    readonly_fields = ['created_at']


class EventInline(admin.TabularInline):
    """Inline für Events in der PlantingCycle-Ansicht"""
    model = Event
    extra = 1
    fields = ['event_type', 'event_date', 'location', 'quantity', 'notes']
    readonly_fields = ['created_at']


class TaskInline(admin.TabularInline):
    """Inline für Tasks in der PlantingCycle-Ansicht"""
    model = Task
    extra = 1
    fields = ['title', 'due_date', 'priority', 'completed']
    readonly_fields = ['created_at']


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['name', 'variety', 'created_at', 'cycle_count']
    list_filter = ['created_at']
    search_fields = ['name', 'variety', 'seed_source']
    inlines = [PlantingCycleInline]

    fieldsets = (
        ('Stammdaten', {
            'fields': ('name', 'variety')
        }),
        ('Herkunft', {
            'fields': ('seed_source',)
        }),
        ('Zusätzliche Informationen', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

    def cycle_count(self, obj):
        """Anzahl der Anbau-Zyklen"""
        return obj.cycles.count()
    cycle_count.short_description = 'Anbau-Zyklen'


@admin.register(PlantingCycle)
class PlantingCycleAdmin(admin.ModelAdmin):
    list_display = ['plant', 'year', 'status', 'seed_saved', 'event_count', 'created_at']
    list_filter = ['year', 'status', 'seed_saved']
    search_fields = ['plant__name', 'plant__variety']
    inlines = [EventInline, TaskInline]

    fieldsets = (
        ('Zuordnung', {
            'fields': ('plant', 'year', 'status')
        }),
        ('Saatgutgewinnung', {
            'fields': ('seed_saved', 'seed_saved_notes')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

    def event_count(self, obj):
        """Anzahl der Ereignisse"""
        return obj.events.count()
    event_count.short_description = 'Ereignisse'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'planting_cycle',
        'event_type',
        'event_date',
        'location',
        'quantity',
        'created_at'
    ]
    list_filter = ['event_type', 'event_date', 'planting_cycle__year']
    search_fields = [
        'planting_cycle__plant__name',
        'location',
        'notes'
    ]
    date_hierarchy = 'event_date'

    fieldsets = (
        ('Ereignis', {
            'fields': ('planting_cycle', 'event_type', 'event_date')
        }),
        ('Details', {
            'fields': ('location', 'quantity', 'notes')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'planting_cycle',
        'due_date',
        'priority',
        'completed',
        'completed_at'
    ]
    list_filter = ['completed', 'priority', 'due_date']
    search_fields = ['title', 'description', 'planting_cycle__plant__name']
    date_hierarchy = 'due_date'
    actions = ['mark_completed', 'mark_incomplete']

    fieldsets = (
        ('Aufgabe', {
            'fields': ('title', 'description', 'planting_cycle')
        }),
        ('Planung', {
            'fields': ('due_date', 'priority')
        }),
        ('Status', {
            'fields': ('completed', 'completed_at')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'completed_at']

    def mark_completed(self, request, queryset):
        """Aufgaben als erledigt markieren"""
        updated = queryset.update(completed=True)
        self.message_user(request, f'{updated} Aufgabe(n) als erledigt markiert.')
    mark_completed.short_description = 'Als erledigt markieren'

    def mark_incomplete(self, request, queryset):
        """Aufgaben als nicht erledigt markieren"""
        updated = queryset.update(completed=False, completed_at=None)
        self.message_user(request, f'{updated} Aufgabe(n) als nicht erledigt markiert.')
    mark_incomplete.short_description = 'Als nicht erledigt markieren'


# Admin-Site Anpassungen
admin.site.site_header = 'Gartenpflanzen Tracker'
admin.site.site_title = 'Garden Tracker Admin'
admin.site.index_title = 'Verwaltung'
