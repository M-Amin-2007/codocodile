# Generated by Django 4.2.4 on 2023-10-26 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_active_myuser_email_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationcodes',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
