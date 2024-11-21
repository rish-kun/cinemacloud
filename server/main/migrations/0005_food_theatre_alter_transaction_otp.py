# Generated by Django 5.1.3 on 2024-11-15 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_transaction_otp_verificationquery'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='theatre',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main.theatre'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='otp',
            field=models.IntegerField(default=104337, editable=False),
        ),
    ]