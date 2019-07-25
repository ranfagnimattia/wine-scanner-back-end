from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Wine(models.Model):
    type = models.CharField(max_length=200)

    def __str__(self):
        return self.type


class WeatherHistory(models.Model):
    wine = models.ForeignKey(Wine, on_delete=models.CASCADE)
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
        return self.date.strftime('%m/%d/%Y') + '-' + self.wine.type


class VintageRating(models.Model):
    wine = models.ForeignKey(Wine, on_delete=models.CASCADE)
    year = models.IntegerField()
    rating = models.FloatField(
        validators=[
            MaxValueValidator(5.0),
            MinValueValidator(1.0)
        ]
    )

    def __str__(self):
        return str(self.year) + '-' + self.wine.type


class SensorHistory(models.Model):
    date = models.DateField()
    temperatureAvg = models.FloatField()
    temperatureMax = models.FloatField()
    temperatureMin = models.FloatField()
    humidityAvg = models.FloatField()
    humidityMax = models.FloatField()
    humidityMin = models.FloatField()
    dewPointAvg = models.FloatField(default=None, blank=True, null=True)
    dewPointMax = models.FloatField(default=None, blank=True, null=True)
    dewPointMin = models.FloatField(default=None, blank=True, null=True)
    upperLeafWetnessHours = models.FloatField(default=None, blank=True, null=True)
    upperLeafWetnessMax = models.FloatField(default=None, blank=True, null=True)
    upperLeafWetnessMin = models.FloatField(default=None, blank=True, null=True)
    lowerLeafWetnessHours = models.FloatField(default=None, blank=True, null=True)
    lowerLeafWetnessMax = models.FloatField(default=None, blank=True, null=True)
    lowerLeafWetnessMin = models.FloatField(default=None, blank=True, null=True)
    rain = models.FloatField()
    windSpeedAvg = models.FloatField()
    windSpeedMax = models.FloatField()
    windDirection = models.FloatField(default=None, blank=True, null=True)

    def __str__(self):
        return self.date.strftime('%m/%d/%Y')
