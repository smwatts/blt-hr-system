# Generated by Django 2.0.8 on 2019-02-21 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blt_hr_system', '0002_auto_20190219_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc_read_req',
            name='read',
            field=models.ManyToManyField(to='blt_hr_system.training_docs'),
        ),
        migrations.AlterField(
            model_name='doc_submit_req',
            name='submitted',
            field=models.ManyToManyField(to='blt_hr_system.training_docs'),
        ),
    ]
