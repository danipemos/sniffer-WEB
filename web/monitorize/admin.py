from django.contrib import admin
from .forms import DeviceChangeForm, DeviceCreationForm, FileCreationForm, FileChangeForm
from .models import Device, File


class DeviceAdmin(admin.ModelAdmin):
    form = DeviceChangeForm
    add_form = DeviceCreationForm
    list_display = ["hostname", "ip", "descripcion"]  # Corrected field name
    search_fields = ["hostname", "ip"]
    ordering = ["hostname"]
    filter_horizontal = []
    fieldsets = [
        (None, {"fields": ["hostname", "ip"]}),
        ("Description", {"fields": ["descripcion"]}),
    ]
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["hostname", "ip"]}),
        ("Description", {"fields": ["descripcion"]}),
    ]

class FileAdmin(admin.ModelAdmin):
    form = FileChangeForm
    add_form = FileCreationForm
    list_display = ["name", "file", "device", "encryption"]
    search_fields = ["name", "file", "device"]
    ordering = ["name"]
    filter_horizontal = []
    fieldsets = [
        (None, {"fields": ["file", "device", ]}),
    ]
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["file", "device", ]}),
    ]


admin.site.register(File, FileAdmin)
admin.site.register(Device, DeviceAdmin)