from django.db import models
from django.utils import timezone


class EquipmentDataset(models.Model):
    """Model to store metadata about uploaded datasets"""
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    total_count = models.IntegerField()
    file_name = models.CharField(max_length=255)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class Equipment(models.Model):
    """Model to store individual equipment records"""
    dataset = models.ForeignKey(EquipmentDataset, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
