from django.db import models
import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Device(models.Model):
    hostname = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.hostname

class PrivateKey(models.Model):
    name = models.CharField(max_length=255)
    key = models.FileField(upload_to='private_keys/')

    def __str__(self):
        return self.name

def file_upload_path(instance, filename):
    hostname = instance.device.hostname

    if "encrypted" in filename:
        folder = f"files/{hostname}/encrypted"
        instance.encryption = "encrypted"
    elif ".zip" in filename:
        folder = f"files/{hostname}/zip"
        instance.encryption = "zip"
    else:
        folder = f"files/{hostname}/decrypted"
        instance.encryption = "decrypted"

    return os.path.join(folder, filename)

class File(models.Model):
    name = models.CharField(max_length=255)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload_path)
    encryption = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Notificar al grupo WebSocket correspondiente
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"files_{self.device.hostname}",
            {
                "type": "new_file",
                "data": {
                    "name": self.name,
                    "encryption": self.encryption,
                },
            }
        )