from django.db import models

class Device(models.Model):
    hostname = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    descripcion = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname

class PrivateKey(models.Model):
    name = models.CharField(max_length=255)
    key = models.FileField(upload_to='private_keys/')
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
