from django import forms
from .models import Device, File
from django.core.exceptions import ValidationError
import gnupg
from django.conf import settings
# Inicializa el objeto GPG
gpg = gnupg.GPG(gnupghome=settings.GNUPG_HOME)

class DeviceChangeForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ("hostname", "ip", "descripcion")

    def clean_hostname(self):
        hostname = self.cleaned_data.get("hostname")
        device_id = self.instance.id
        if Device.objects.filter(hostname=hostname).exclude(id=device_id).exists():
            raise ValidationError("A device with this hostname already exists.")
        return hostname
    
    def clean_ip(self):
        ip = self.cleaned_data.get("ip")
        device_id = self.instance.id
        if Device.objects.filter(ip=ip).exclude(id=device_id).exists():
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
    
    
class PrivateKeyCreationForm(forms.Form):
    name = forms.CharField(label="Name", max_length=255, required=True)
    email = forms.EmailField(label="Email", max_length=255, required=True)
    algorithm = forms.ChoiceField(
        choices=[
            ('RSA', 'RSA'),
            ('DSA', 'DSA'),
        ],
        required=True
    )
    size = forms.IntegerField(label="Size", required=True)
    comment = forms.CharField(label="Comment", widget=forms.Textarea, required=False)
    passphrase = forms.CharField(label="Passphrase", widget=forms.PasswordInput, required=True)
    expiration_date = forms.CharField(label="Expiration Date", required=True, help_text="Format: 1y, 6m, 2w, etc. 0 for no expiration")

    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar longitud de clave válida según algoritmo
        algorithm = cleaned_data.get('algorithm')
        key_size = cleaned_data.get('size')
        
        if algorithm == 'RSA' and (key_size < 1024 or key_size > 4096):
            raise ValidationError({"size": "El tamaño de clave RSA debe estar entre 1024 y 4096 bits"})
        
        if algorithm == 'DSA' and (key_size < 1024 or key_size > 3072):
            raise ValidationError({"size": "El tamaño de clave DSA debe ser 1024 bits"})
        
        # Verificar formato de fecha de expiración
        expiration = cleaned_data.get('expiration_date')
        if expiration != '0':
            if not any(expiration.endswith(unit) for unit in ['d', 'w', 'm', 'y']):
                raise ValidationError({"expiration_date": "Formato inválido. Use: 1y, 6m, 2w, 5d o 0"})
            
            try:
                value = int(expiration[:-1])
                if value <= 0:
                    raise ValidationError({"expiration_date": "El valor debe ser positivo"})
            except ValueError:
                raise ValidationError({"expiration_date": "Formato inválido. Use: 1y, 6m, 2w, 5d o 0"})
        
        return cleaned_data

    def save(self, commit=True):
        input_data = {
            'name_real': self.cleaned_data['name'],
            'name_email': self.cleaned_data['email'],
            'key_type': self.cleaned_data['algorithm'],
            'key_length': self.cleaned_data['size'],
            'passphrase': self.cleaned_data['passphrase'],
            'expire_date': self.cleaned_data['expiration_date'],
        }
        if self.cleaned_data['comment']:
            input_data['name_comment'] = self.cleaned_data['comment']
        key = gpg.gen_key(gpg.gen_key_input(**input_data))
        if not key.fingerprint:
            raise ValidationError("Failed to generate key"+key.stderr)
        else:
            return key.fingerprint

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