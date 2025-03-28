from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, UserChangeForm
from .models import OurUser

# Clase personalizada para administrar el modelo OurUser
class UserAdmin(BaseUserAdmin):
    # Campos que se mostrarán en la lista de usuarios
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ["username", "is_superuser"]
    list_filter = ["is_superuser"]
    
    # Campos que se mostrarán al editar un usuario
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Permissions", {"fields": ["is_active", "is_superuser"]}),
        ("Important dates", {"fields": ["last_login", "date_joined"]}),
    ]
    
    # Campos que se mostrarán al crear un usuario
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "password1", "password2"],
            },
        ),
    ]
    
    search_fields = ["username"]
    ordering = ["username"]
    filter_horizontal = []


admin.site.register(OurUser, UserAdmin)


admin.site.unregister(Group)
