# Generated by Django 2.0.8 on 2018-12-06 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0005_auto_20181206_1302'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee_group',
            old_name='region',
            new_name='location',
        ),
    ]