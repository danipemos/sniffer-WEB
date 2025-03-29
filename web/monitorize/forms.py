from django import forms
from .models import Device, PrivateKey
from django.core.exceptions import ValidationError
import os

class DeviceChangeForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ("hostname", "ip", "username", "password", "descripcion")

    def save(self, commit=True):
        device = super().save(commit=False)
        device.hostname = self.cleaned_data["hostname"]
        device.ip = self.cleaned_data["ip"]
        device.username = self.cleaned_data["username"]
        device.password = self.cleaned_data["password"]
        device.descripcion = self.cleaned_data.get("descripcion", "")
        if commit:
            device.save()
        return device


class DeviceCreationForm(forms.ModelForm):
    hostname = forms.CharField(label="Hostname", max_length=255, required=True)
    ip = forms.GenericIPAddressField(label="IP Address", required=True)
    username = forms.CharField(label="Username", max_length=150, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    descripcion = forms.CharField(label="Description", widget=forms.Textarea, required=False)
    hostname.widget.attrs.update({"placeholder": "Hostname"})
    ip.widget.attrs.update({"placeholder": "IP Address"})
    username.widget.attrs.update({"placeholder": "Username"})
    password.widget.attrs.update({"placeholder": "Password"})
    descripcion.widget.attrs.update({"placeholder": "Description"})
    class Meta:
        model = Device
        fields = ("hostname", "ip", "username", "password", "descripcion")

    def save(self, commit=True):
        device = super().save(commit=False)
        device.hostname = self.cleaned_data["hostname"]
        device.ip = self.cleaned_data["ip"]
        device.username = self.cleaned_data["username"]
        device.password = self.cleaned_data["password"]
        device.descripcion = self.cleaned_data.get("descripcion", "")
        if commit:
            device.save()
        return device
    
class PrivateKeyChangeForm(forms.ModelForm):
    class Meta:
        model = PrivateKey
        fields = ("name", "key")

    def save(self, commit=True):
        private_key = super().save(commit=False)
        if private_key.pk: 
            old_private_key = PrivateKey.objects.get(pk=private_key.pk)
            if old_private_key.key and old_private_key.key != self.cleaned_data["key"]:
                if os.path.isfile(old_private_key.key.path):
                    os.remove(old_private_key.key.path)
        private_key.name = self.cleaned_data["name"]
        private_key.key = self.cleaned_data["key"]
        if commit:
            private_key.save()
        return private_key
    
class PrivateKeyCreationForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=255, required=True)
    key = forms.FileField(label="Private Key File", required=True)
    name.widget.attrs.update({"placeholder": "Name"})
    key.widget.attrs.update({"placeholder": "Private Key File"})
    
    class Meta:
        model = PrivateKey
        fields = ("name", "key")

    def save(self, commit=True):
        private_key = super().save(commit=False)
        private_key.name = self.cleaned_data["name"]
        private_key.key = self.cleaned_data["key"]
        if commit:
            private_key.save()
        return private_key
