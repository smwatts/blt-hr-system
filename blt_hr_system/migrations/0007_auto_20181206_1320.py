# Generated by Django 2.0.8 on 2018-12-06 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0006_auto_20181206_1316'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company_info',
            old_name='region',
            new_name='location',
        ),
        migrations.RenameField(
            model_name='holiday',
            old_name='region',
            new_name='location',
        ),
    ]
