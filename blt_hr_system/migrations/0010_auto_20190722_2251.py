# Generated by Django 2.2.3 on 2019-07-23 03:51

import blt_hr_system.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blt_hr_system', '0009_auto_20190721_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='perf_forms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_name', models.CharField(max_length=200)),
                ('upload', models.FileField(upload_to=blt_hr_system.models.RandomFileName('media/perf_form/'))),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='emp_perf_forms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('upload_name', models.CharField(max_length=200)),
                ('upload', models.FileField(upload_to=blt_hr_system.models.RandomFileName('media/emp_perf_form/'))),
                ('manager_comment', models.CharField(max_length=5000)),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='perf_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='blt_hr_system.perf_forms'),
        ),
    ]
