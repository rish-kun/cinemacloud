# Generated by Django 5.1.3 on 2024-11-14 07:01

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_show_screen_alter_transaction_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='theatre',
            name='default_screen_id',
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='otp',
            field=models.IntegerField(default=132006, editable=False),
        ),
        migrations.CreateModel(
            name='Screen',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('screen_number', models.IntegerField()),
                ('seats', models.JSONField(default=None, null=True)),
                ('theatre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.theatre')),
            ],
        ),
        migrations.AlterField(
            model_name='show',
            name='screen',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.screen'),
        ),
    ]
