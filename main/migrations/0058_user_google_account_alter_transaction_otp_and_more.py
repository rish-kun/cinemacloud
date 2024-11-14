# Generated by Django 5.1.3 on 2024-11-14 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_alter_transaction_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='google_account',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='otp',
            field=models.IntegerField(default=652727, editable=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.BinaryField(max_length=255, null=True),
        ),
    ]
