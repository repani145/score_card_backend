# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django_mysql.models import EnumField
# from django_mysql.models.fields import EnumField
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Now
from django.db import models
import uuid
from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_staff(self, mobile, password=None, **extra_fields):
        try:
            if not mobile:
                raise ValueError('The Mobile field must be set.')
            mobile = mobile
            if not extra_fields['user_type']:
                extra_fields.setdefault('user_type', 'staff')
            user = self.model(mobile=mobile, **extra_fields)
            if password:
                user.set_password(password)
            user.save(using=self._db)
            return user
        except Exception as e:
            raise ValueError(str(e))

    def create_admin(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError('The mobile field must be set.')
        mobile = mobile
        user = self.model(mobile=mobile, user_type='admin', **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'super_admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_staff(mobile, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    USER_CHOICES = [
        ('super_admin', 'Suer Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    # ['super_admin','admin','staff','user']
    
    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    mobile = models.CharField(max_length=15, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=True, blank=False)
    password = models.CharField(max_length=255, null=True, blank=False)
    user_type = models.CharField(choices=USER_CHOICES,max_length=12, default='staff')
    groups = models.ManyToManyField('auth.Group', related_name='user_groups', blank=True)
    permissions = models.ManyToManyField('auth.Permission', related_name='user_permissions', blank=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    modified_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','mobile']

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return self.full_name
    
    def save(self, *args, **kwargs):
        """Ensure password is hashed before saving."""
        if self.pk is None or not CustomUser.objects.filter(pk=self.pk).exists():
            self.set_password(self.password)  # Hash password only on creation
        super().save(*args, **kwargs)

    def last_updated(self):
        return self.modified_at.strftime("%d %b %y %I:%M %p")

