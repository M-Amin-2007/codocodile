# Generated by Django 4.2.6 on 2023-10-25 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_activationcodes'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]