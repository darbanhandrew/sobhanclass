# Generated by Django 3.2.10 on 2021-12-19 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_user_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('can_read', "Can read the this object's info."), ('can_write', "Can modify this object's info.")]},
        ),
    ]
