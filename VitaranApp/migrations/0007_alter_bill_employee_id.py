# Generated by Django 4.0.5 on 2022-10-09 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VitaranApp', '0006_remove_profile_phone_remove_profile_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='Employee_ID',
            field=models.CharField(default='0', max_length=15),
        ),
    ]