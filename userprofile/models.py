from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from graphene_django_plus.models import GuardedModel

# Create your models here.


class User(AbstractUser, GuardedModel):
    class Meta:
        # guardian permissions for this model
        permissions = [
            ('can_read', "Can read the this object's info."),
            ('can_write', "Can modify this object's info."),
        ]
    phone_number = models.CharField(max_length=10, blank=True, null=True)
