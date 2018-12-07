# Generated by Django 2.0.8 on 2018-12-07 06:30

import blt_hr_system.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0007_auto_20181206_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee_certification',
            name='cert_doc',
        ),
        migrations.RemoveField(
            model_name='employee_group',
            name='location',
        ),
        migrations.AddField(
            model_name='certs_maintained',
            name='location',
            field=models.ManyToManyField(to='blt_hr_system.company_info'),
        ),
        migrations.AddField(
            model_name='employee_certification',
            name='upload',
            field=models.FileField(blank=True, null=True, upload_to=blt_hr_system.models.RandomFileName('media/certification/')),
        ),
        migrations.RemoveField(
            model_name='certs_maintained',
            name='employee_group',
        ),
        migrations.AddField(
            model_name='certs_maintained',
            name='employee_group',
            field=models.ManyToManyField(to='blt_hr_system.employee_group'),
        ),
    ]
