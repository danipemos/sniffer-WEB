from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class OurUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('User must have a username')
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.save(using=self._db)
        return user

class OurUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)

    objects = OurUserManager()
    USERNAME_FIELD = 'username'

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def is_staff(self):
        return self.is_superuser
    
    @property
    def is_active(self):
        return True
    @property
    def is_superuser(self):
        return True

    def __str__(self):
        return self.username
