import json

import math
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Sensor(models.Model):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    min = models.FloatField(default=None, blank=True, null=True)
    max = models.FloatField(default=None, blank=True, null=True)
    values = models.BooleanField(default=True)
    tot = models.BooleanField(default=False)
    startTestSet = models.DateField(default=None, blank=True, null=True)

    def get_measures(self):
        measures = []
        if self.tot:
            measures.append('tot')
        if self.values:
            measures.extend(['avg', 'max', 'min'])
        return measures

    def get_prediction_measures(self):
        if self.startTestSet is None:
            return []
        if self.tot:
            return ['tot']
        if self.values:
            return ['avg', 'max', 'min']
        return []

    def to_js(self):
        return {'id': self.id, 'name': self.name, 'unit': self.unit, 'icon': self.icon,
                'values': self.values, 'tot': self.tot, 'min': self.min, 'max': self.max}

    def __str__(self):
        return self.name


class DailyData(models.Model):
    date = models.DateField()
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    avg = models.FloatField(default=None, blank=True, null=True)
    min = models.FloatField(default=None, blank=True, null=True)
    max = models.FloatField(default=None, blank=True, null=True)
    minTime = models.TimeField(default=None, blank=True, null=True)
    maxTime = models.TimeField(default=None, blank=True, null=True)
    tot = models.FloatField(default=None, blank=True, null=True)

    class Meta:
        unique_together = ('date', 'sensor')

    def __str__(self):
        return self.date.strftime('%d/%m/%Y') + '-' + str(self.sensor)


class RealTimeData(models.Model):
    time = models.DateTimeField()
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        unique_together = ('time', 'sensor')

    def __str__(self):
        return self.time.strftime('%d/%m/%Y %H:%M') + '-' + str(self.sensor)


class PredictionMethod(models.Model):
    name = models.CharField(max_length=50)
    reset = models.BooleanField(default=False)
    defaultParams = models.TextField(default='')

    def get_params(self):
        if self.defaultParams == '' or self.defaultParams == '{}':
            return {}
        else:
            return json.loads(self.defaultParams)

    def __str__(self):
        return self.name


class PredictionParams(models.Model):
    method = models.ForeignKey(PredictionMethod, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    params = models.TextField(default='')

    def get_params(self):
        if self.params == '' or self.params == '{}':
            return {}
        else:
            return json.loads(self.params)

    class Meta:
        unique_together = ('sensor', 'method')

    def __str__(self):
        return str(self.method) + '-' + str(self.sensor)


class Prediction(models.Model):
    MEASURES = (("tot", "tot"),
                ("avg", "avg"),
                ("max", "max"),
                ("min", "min"))

    date = models.DateField()
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    measure = models.CharField(choices=MEASURES, max_length=3)
    actual = models.FloatField()
    prediction = models.FloatField()
    mean = models.FloatField()
    var = models.FloatField()
    limit = models.FloatField()
    count = models.IntegerField()
    anomaly = models.BooleanField()
    method = models.ForeignKey(PredictionMethod, on_delete=models.CASCADE)

    def check_limits(self):
        if self.sensor.min is not None and self.prediction < self.sensor.min:
            self.prediction = self.sensor.min
        if self.sensor.max is not None and self.prediction > self.sensor.max:
            self.prediction = self.sensor.max

    def get_mse(self):
        return math.sqrt(self.var / self.count)

    class Meta:
        unique_together = ('date', 'sensor', 'measure', 'method')

    def __str__(self):
        return self.date.strftime('%d/%m/%Y') + '-' + str(self.sensor) + '-' + \
               str(self.measure) + '-' + str(self.method)


class VintageRating(models.Model):
    year = models.IntegerField(primary_key=True)
    rating = models.FloatField(
        validators=[
            MaxValueValidator(5.0),
            MinValueValidator(1.0)
        ]
    )

    def __str__(self):
        return str(self.year) + '-' + str(self.rating)


class WeatherHistory(models.Model):
    date = models.DateField()
    time = models.IntegerField()
    icon = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    precipitationType = models.CharField(max_length=200)
    precipitationIntensity = models.FloatField()
    precipitationIntensityMax = models.FloatField()
    precipitationIntensityMaxTime = models.IntegerField()
    precipitationProbability = models.FloatField()
    precipitationAccumulation = models.FloatField()
    uvIndex = models.IntegerField()
    uvIndexTime = models.IntegerField()
    sunriseTime = models.IntegerField()
    sunsetTime = models.IntegerField()
    temperatureMax = models.FloatField()
    temperatureMin = models.FloatField()
    apparentTemperatureMax = models.FloatField()
    apparentTemperatureMin = models.FloatField()
    windBearing = models.IntegerField()
    apparentTemperatureMaxTime = models.IntegerField()
    apparentTemperatureMinTime = models.IntegerField()
    temperatureMinTime = models.IntegerField()
    temperatureMaxTime = models.IntegerField()
    humidity = models.FloatField()
    cloudCover = models.FloatField()
    dewPoint = models.FloatField()
    windSpeed = models.FloatField()
    moonPhase = models.FloatField()
    pressure = models.FloatField()
    visibility = models.FloatField()
    temperatureHigh = models.FloatField()
    temperatureLow = models.FloatField()
    temperatureHighTime = models.IntegerField()
    temperatureLowTime = models.IntegerField()
    apparentTemperatureHigh = models.FloatField()
    apparentTemperatureLow = models.FloatField()
    apparentTemperatureHighTime = models.IntegerField()
    apparentTemperatureLowTime = models.IntegerField()

    def __str__(self):
        return self.date.strftime('%d/%m/%Y')


class LastUpdate(models.Model):
    type = models.CharField(primary_key=True, max_length=10)
    time = models.DateTimeField()

    def __str__(self):
        return self.type + '-' + self.time.strftime('%d/%m/%Y %H:%M')
