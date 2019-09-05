# Generated by Django 2.2.3 on 2019-09-05 15:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('WineApp', '0010_auto_20190822_1806'),
    ]

    operations = [
        migrations.CreateModel(
            name='HourlyAirHumidity',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyAirTemperature',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyDewPoint',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyGroundHumidity',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyGroundTemperature',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyGustOfWind',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyLowerLeafWetness',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyPressure',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyRain',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlySolarRadiation',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyUpperLeafWetness',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyWindDirection',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='HourlyWindSpeed',
            fields=[
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('value', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='sensor',
            name='hourlyTable',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]