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

    list_display = ["username", "is_superuser","is_active", "date_joined", "last_login"]
    list_filter = ["is_superuser", "is_active"]
    
    # Campos que se mostrarán al editar un usuario
    fieldsets = [
        (None, {"fields": ["username"]}),
        ("Permissions", {"fields": ["is_active", "is_superuser"]}),
        ("Change Password", {"fields": ["new_password1", "new_password2"]}),
    ]
    
    # Campos que se mostrarán al crear un usuario
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "password1", "password2", "is_superuser"],
            },
        ),
    ]
    
    search_fields = ["username"]
    ordering = ["username"]
    filter_horizontal = []


admin.site.register(OurUser, UserAdmin)


admin.site.unregister(Group)
