# Generated by Django 4.1.1 on 2022-09-25 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VitaranApp', '0002_bill_net_billed_amount_bill_payable_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='OTP',
            field=models.CharField(default=0, max_length=4),
        ),
    ]
