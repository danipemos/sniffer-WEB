from django.contrib import admin
from .forms import DeviceChangeForm, DeviceCreationForm, PrivateKeyChangeForm, PrivateKeyCreationForm, FileCreationForm, FileChangeForm
from .models import Device, PrivateKey,File


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


class PrivateKeyAdmin(admin.ModelAdmin):
    form = PrivateKeyChangeForm
    add_form = PrivateKeyCreationForm
    list_display = ["name", "key"]  # Corrected field name
    search_fields = ["name", "key"]
    ordering = ["name"]
    filter_horizontal = []
    fieldsets = [
        (None, {"fields": ["name", "key"]}),
    ]
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["name", "key"]}),
    ]

class FileAdmin(admin.ModelAdmin):
    form = FileChangeForm
    add_form = FileCreationForm
    list_display = ["name","file", "device", "encryption"]
    search_fields = ["name","file","device"]
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
admin.site.register(PrivateKey, PrivateKeyAdmin)