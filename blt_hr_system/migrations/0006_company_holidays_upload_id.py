# Generated by Django 2.2.3 on 2019-07-19 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0005_control_date_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_holidays',
            name='upload_id',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
