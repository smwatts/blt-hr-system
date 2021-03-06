# Generated by Django 2.2.3 on 2019-07-19 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='company_holidays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('holiday_name', models.CharField(max_length=200)),
                ('holiday_date', models.DateField()),
                ('is_finalized', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='employee_absence',
            name='is_admin_approved',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='employee_absence',
            name='is_manager_approved',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='employee_certification',
            name='is_approved',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='office_staff',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='training_docs',
            name='active_doc',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='vaction_allocation',
            name='is_increased',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
