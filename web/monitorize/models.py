from django.db import models
import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Device(models.Model):
    hostname = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    descripcion = models.TextField(blank=True, null=True)
    ssh_private_key = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.hostname
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "devices",  # Grupo general para la lista de dispositivos
                {
                    "type": "new_device",
                    "data": {
                        "id": self.id,
                        "hostname": self.hostname,
                        "ip": self.ip,
                        "descripcion": self.descripcion,
                    },
                }
            )

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
                    "id": self.id,  # Add this line to include the file ID
                    "name": self.name,
                    "encryption": self.encryption,
                },
            }
        )

@receiver(post_delete, sender=File)
def delete_file_on_instance_delete(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

