# Generated by Django 3.1.6 on 2021-04-24 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_auto_20210423_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='is_best',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
