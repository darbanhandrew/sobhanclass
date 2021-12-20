from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from graphene_django_plus.models import GuardedModel
from random import randint
# Create your models here.


class User(AbstractUser, GuardedModel):
    class Meta:
        # guardian permissions for this model
        permissions = [
            ('can_read', "Can read the this object's info."),
            ('can_write', "Can modify this object's info."),
        ]
    phone_number = models.CharField(max_length=10, blank=True, null=True)


class OTP(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.otp

    def save(self, *args, **kwargs):
        if not self.id:
            self.generate_otp()
        super().save(*args, **kwargs)

    def generate_otp(self):
        n = 5
        range_start = 10**(n-1)
        range_end = (10**n)-1
        self.otp = str(randint(range_start, range_end))


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        OTP.objects.create(user=instance)


@receiver(post_save, sender=OTP)
def verify_otp(sender, instance, **kwargs):
    if instance.is_verified:
        instance.user.is_active = True
        instance.user.save()
