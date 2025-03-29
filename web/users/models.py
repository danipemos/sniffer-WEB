from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class OurUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('User must have a username')
        user = self.model(username=username)
        user.set_password(password)
        user.is_active = True  # Default value for is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.save(using=self._db)
        return user

class OurUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = OurUserManager()
    USERNAME_FIELD = 'username'

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return self.username
