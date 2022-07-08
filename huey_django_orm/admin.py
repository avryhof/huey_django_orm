from django.contrib import admin

from huey_django_orm.models import HueyKv, HueySchedule, HueyTask


@admin.register(HueyKv)
class HueyKvAdmin(admin.ModelAdmin):
    list_display = ("queue", "key", "created")
    readonly_fields = ("queue", "key", "value", "created",)


@admin.register(HueySchedule)
class HueyScheduleAdmin(admin.ModelAdmin):
    list_display = ("queue", "timestamp", "created",)
    readonly_fields = ("queue", "data", "timestamp", "created",)


@admin.register(HueyTask)
class HueyTaskAdmin(admin.ModelAdmin):
    list_display = ("queue", "priority", "created",)
    readonly_fields = ("queue", "data", "priority", "created",)