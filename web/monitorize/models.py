from django.db import models

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
