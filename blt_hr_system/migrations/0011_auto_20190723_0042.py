# Generated by Django 2.2.3 on 2019-07-23 05:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0010_auto_20190722_2251'),
    ]

    operations = [
        migrations.CreateModel(
            name='perf_cat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RenameField(
            model_name='emp_perf_forms',
            old_name='employee_id',
            new_name='employee',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='perf_form',
        ),
        migrations.AddField(
            model_name='perf_forms',
            name='perf_cat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blt_hr_system.perf_cat'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='perf_cat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='blt_hr_system.perf_cat'),
        ),
    ]
