# Generated by Django 2.2.3 on 2019-08-18 16:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('WineApp', '0005_prediction_predictionmethod'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictionmethod',
            name='reset',
            field=models.BooleanField(default=False),
        ),
    ]
