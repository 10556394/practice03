# Generated by Django 3.1.6 on 2021-04-28 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_auto_20210429_0650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(max_length=25),
        ),
        migrations.AlterField(
            model_name='reply',
            name='body',
            field=models.TextField(max_length=25),
        ),
    ]
