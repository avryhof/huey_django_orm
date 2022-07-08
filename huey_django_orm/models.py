from django.db import models


class HueyKv(models.Model):
    queue = models.TextField(blank=False, null=False, default="default")
    key = models.TextField(blank=True, null=True)
    value = models.BinaryField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class HueySchedule(models.Model):
    queue = models.TextField(blank=False, null=False, default="default")
    data = models.BinaryField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ("timestamp",)


class HueyTask(models.Model):
    queue = models.TextField(blank=False, null=False, default="default")
    data = models.BinaryField(blank=True, null=True)
    priority = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ("-priority", "id")
