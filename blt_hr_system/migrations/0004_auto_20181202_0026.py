# Generated by Django 2.0.8 on 2018-12-02 05:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blt_hr_system', '0003_training_docs_upload'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='email',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_name',
        ),
        migrations.AddField(
            model_name='employee_group',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='employee_group',
            name='group_description',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='employee_group',
            name='group_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
