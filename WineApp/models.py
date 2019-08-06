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
    activeFrom = models.DateField()

    # predictionFrom = models.DateField(default=None, blank=True, null=True)

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
