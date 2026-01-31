from django.db import models
from django.utils import timezone


class Plant(models.Model):
    """Pflanze mit Stammdaten"""
    name = models.CharField(max_length=200, verbose_name='Pflanzenname')
    variety = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Sorte/Varietät',
        help_text='z.B. "Ochsenherz", "Cherry"'
    )
    seed_source = models.TextField(
        blank=True,
        verbose_name='Samenherkunft',
        help_text='Wo wurden die Samen gekauft oder gewonnen?'
    )
    notes = models.TextField(blank=True, verbose_name='Notizen')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')

    class Meta:
        verbose_name = 'Pflanze'
        verbose_name_plural = 'Pflanzen'
        ordering = ['name', 'variety']

    def __str__(self):
        if self.variety:
            return f"{self.name} ({self.variety})"
        return self.name


class PlantingCycle(models.Model):
    """Anbau-Zyklus einer Pflanze für ein bestimmtes Jahr"""

    STATUS_CHOICES = [
        ('planning', 'Planung'),
        ('sowing', 'Säen'),
        ('germinating', 'Keimung'),
        ('growing', 'Wachstum'),
        ('planted_out', 'Ausgepflanzt'),
        ('harvesting', 'Ernte'),
        ('finished', 'Abgeschlossen'),
    ]

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='cycles',
        verbose_name='Pflanze'
    )
    year = models.IntegerField(
        default=timezone.now().year,
        verbose_name='Anbaujahr'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        verbose_name='Status'
    )
    seed_saved = models.BooleanField(
        default=False,
        verbose_name='Samen gewonnen?',
        help_text='Wurden Samen für das nächste Jahr gewonnen?'
    )
    seed_saved_notes = models.TextField(
        blank=True,
        verbose_name='Notizen zur Saatgutgewinnung'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')

    class Meta:
        verbose_name = 'Anbau-Zyklus'
        verbose_name_plural = 'Anbau-Zyklen'
        ordering = ['-year', 'plant__name']
        unique_together = ['plant', 'year']

    def __str__(self):
        return f"{self.plant.name} - {self.year}"


class Event(models.Model):
    """Ereignis im Lebenszyklus einer Pflanze"""

    EVENT_TYPE_CHOICES = [
        ('sowing', 'Aussaat'),
        ('germination', 'Keimung'),
        ('transplanting', 'Umpflanzen'),
        ('watering', 'Gießen'),
        ('fertilizing', 'Düngen'),
        ('planting_out', 'Ins Beet pflanzen'),
        ('harvest', 'Ernte'),
        ('pruning', 'Schneiden'),
        ('other', 'Sonstiges'),
    ]

    planting_cycle = models.ForeignKey(
        PlantingCycle,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Anbau-Zyklus'
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name='Ereignistyp'
    )
    event_date = models.DateField(
        default=timezone.now,
        verbose_name='Datum'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ort',
        help_text='z.B. "Topf 5cm", "Beet A", "Gewächshaus"'
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Menge',
        help_text='Bei Bewässerung: Liter, bei Ernte: kg/Stück'
    )
    notes = models.TextField(blank=True, verbose_name='Notizen')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')

    class Meta:
        verbose_name = 'Ereignis'
        verbose_name_plural = 'Ereignisse'
        ordering = ['-event_date', '-created_at']

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.planting_cycle.plant.name} ({self.event_date})"


class Task(models.Model):
    """Aufgabe - manuell oder automatisch generiert"""

    PRIORITY_CHOICES = [
        ('low', 'Niedrig'),
        ('medium', 'Mittel'),
        ('high', 'Hoch'),
    ]

    planting_cycle = models.ForeignKey(
        PlantingCycle,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        verbose_name='Anbau-Zyklus',
        help_text='Optional: Verknüpfung mit einem Anbau-Zyklus'
    )
    title = models.CharField(max_length=200, verbose_name='Titel')
    description = models.TextField(blank=True, verbose_name='Beschreibung')
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fälligkeitsdatum'
    )
    completed = models.BooleanField(default=False, verbose_name='Erledigt')
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Erledigt am'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priorität'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')

    class Meta:
        verbose_name = 'Aufgabe'
        verbose_name_plural = 'Aufgaben'
        ordering = ['completed', '-priority', 'due_date']

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.title}"

    def save(self, *args, **kwargs):
        # Automatisch completed_at setzen wenn completed
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)
