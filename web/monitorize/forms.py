from django import forms
from .models import Device, PrivateKey, File
from django.core.exceptions import ValidationError
import os

class DeviceChangeForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ("hostname", "ip", "descripcion")

    def clean_hostname(self):
        hostname = self.cleaned_data.get("hostname")
        if Device.objects.filter(hostname=hostname).exists():
            raise ValidationError("A device with this hostname already exists.")
        return hostname
    
    def clean_ip(self):
        ip = self.cleaned_data.get("ip")
        if Device.objects.filter(ip=ip).exists():
            raise ValidationError("A device with this IP address already exists.")
        return ip

    def save(self, commit=True):
        device = super().save(commit=False)
        device.hostname = self.cleaned_data["hostname"]
        device.ip = self.cleaned_data["ip"]
        device.descripcion = self.cleaned_data.get("descripcion", "")
        if commit:
            device.save()
        return device


class DeviceCreationForm(forms.ModelForm):
    hostname = forms.CharField(label="Hostname", max_length=255, required=True)
    ip = forms.GenericIPAddressField(label="IP Address", required=True)
    descripcion = forms.CharField(label="Description", widget=forms.Textarea, required=False)
    hostname.widget.attrs.update({"placeholder": "Hostname"})
    ip.widget.attrs.update({"placeholder": "IP Address"})
    descripcion.widget.attrs.update({"placeholder": "Description"})
    class Meta:
        model = Device
        fields = ("hostname", "ip", "descripcion")

    def clean_hostname(self):
        hostname = self.cleaned_data.get("hostname")
        if Device.objects.filter(hostname=hostname).exists():
            raise ValidationError("A device with this hostname already exists.")
        return hostname
    
    def clean_ip(self):
        ip = self.cleaned_data.get("ip")
        if Device.objects.filter(ip=ip).exists():
            raise ValidationError("A device with this IP address already exists.")
        return ip
    def save(self, commit=True):
        device = super().save(commit=False)
        device.hostname = self.cleaned_data["hostname"]
        device.ip = self.cleaned_data["ip"]
        device.descripcion = self.cleaned_data.get("descripcion", "")
        if commit:
            device.save()
        return device
    
class PrivateKeyChangeForm(forms.ModelForm):
    class Meta:
        model = PrivateKey
        fields = ("name", "key")

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if PrivateKey.objects.filter(name=name).exists():
            raise ValidationError("A private key with this name already exists.")
        return name
        
    def clean_key(self):
        key = self.cleaned_data.get("key")
        if PrivateKey.objects.filter(key=key).exists():
            raise ValidationError("A private key with this file already exists.")
        return key

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

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if PrivateKey.objects.filter(name=name).exists():
            raise ValidationError("A private key with this name already exists.")
        return name
        
    def clean_key(self):
        key = self.cleaned_data.get("key")
        if PrivateKey.objects.filter(key=key).exists():
            raise ValidationError("A private key with this file already exists.")
        return key

    def save(self, commit=True):
        private_key = super().save(commit=False)
        private_key.name = self.cleaned_data["name"]
        private_key.key = self.cleaned_data["key"]
        if commit:
            private_key.save()
        return private_key

class FileCreationForm(forms.ModelForm):
    file = forms.FileField(label="file", required=True)
    file.widget.attrs.update({"placeholder": "file"})
    device = forms.ModelChoiceField(queryset=Device.objects.all(), label="device", required=True)
    device.widget.attrs.update({"placeholder": "device"})
    class Meta:
        model = File
        fields = ("file", "device")
    
    def save(self, commit = True):
        file= super().save(commit)
        file.file = self.cleaned_data["file"]
        file.device = self.cleaned_data["device"]
        file.name = self.cleaned_data["file"].name
        if commit:
            file.save()
        return file
    

class FileChangeForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ("file","device")
    
    def save(self, commit = True):
        file= super().save(commit)
        file.file = self.cleaned_data["file"]
        file.device = self.cleaned_data["device"]
        file.name = self.cleaned_data["file"].name
        if commit:
            file.save()
        return file