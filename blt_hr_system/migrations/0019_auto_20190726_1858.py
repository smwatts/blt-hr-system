# Generated by Django 2.2.3 on 2019-07-26 23:58

import blt_hr_system.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('blt_hr_system', '0018_extendeduser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emp_perf_forms',
            name='manager_comment',
        ),
        migrations.AddField(
            model_name='emp_perf_forms',
            name='manager_upload',
            field=models.FileField(blank=True, null=True, upload_to=blt_hr_system.models.RandomFileName('media/emp_manager_perf_form/')),
        ),
        migrations.AddField(
            model_name='emp_perf_forms',
            name='manager_upload_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.DeleteModel(
            name='ExtendedUser',
        ),
    ]
