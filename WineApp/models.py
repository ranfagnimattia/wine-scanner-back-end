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
        return self.date.strftime('%d/%m/%Y') + '-' + self.wine.type


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
    airTemperatureAvg = models.FloatField()
    airTemperatureMax = models.FloatField()
    airTemperatureMin = models.FloatField()
    airHumidityAvg = models.FloatField()
    airHumidityMax = models.FloatField()
    airHumidityMin = models.FloatField()
    dewPointAvg = models.FloatField(default=None, blank=True, null=True)
    dewPointMax = models.FloatField(default=None, blank=True, null=True)
    dewPointMin = models.FloatField(default=None, blank=True, null=True)
    upperLeafWetnessHours = models.FloatField(default=None, blank=True, null=True)
    upperLeafWetnessMax = models.FloatField(default=None, blank=True, null=True)
    upperLeafWetnessMin = models.FloatField(default=None, blank=True, null=True)
    lowerLeafWetnessHours = models.FloatField(default=None, blank=True, null=True)
    lowerLeafWetnessMax = models.FloatField(default=None, blank=True, null=True)
    lowerLeafWetnessMin = models.FloatField(default=None, blank=True, null=True)
    rainAvg = models.FloatField()
    windSpeedAvg = models.FloatField()
    windSpeedMax = models.FloatField()
    windDirectionAvg = models.FloatField(default=None, blank=True, null=True)

    def __str__(self):
        return self.date.strftime('%d/%m/%Y')


class DailySensorData(models.Model):
    date = models.DateField(primary_key=True)
    pressureAvg = models.FloatField()
    pressureMax = models.FloatField()
    pressureMaxTime = models.TimeField()
    pressureMin = models.FloatField()
    pressureMinTime = models.TimeField()
    windDirectionAvg = models.FloatField()
    windDirectionMax = models.FloatField()
    windDirectionMaxTime = models.TimeField()
    windDirectionMin = models.FloatField()
    windDirectionMinTime = models.TimeField()
    upperLeafWetnessAvg = models.FloatField()
    upperLeafWetnessMax = models.FloatField()
    upperLeafWetnessMaxTime = models.TimeField()
    upperLeafWetnessMin = models.FloatField()
    upperLeafWetnessMinTime = models.TimeField()
    lowerLeafWetnessAvg = models.FloatField()
    lowerLeafWetnessMax = models.FloatField()
    lowerLeafWetnessMaxTime = models.TimeField()
    lowerLeafWetnessMin = models.FloatField()
    lowerLeafWetnessMinTime = models.TimeField()
    solarRadiationAvg = models.FloatField()
    solarRadiationMax = models.FloatField()
    solarRadiationMaxTime = models.TimeField()
    solarRadiationMin = models.FloatField()
    solarRadiationMinTime = models.TimeField()
    windSpeedAvg = models.FloatField()
    windSpeedMax = models.FloatField()
    windSpeedMaxTime = models.TimeField()
    windSpeedMin = models.FloatField()
    windSpeedMinTime = models.TimeField()
    airTemperatureAvg = models.FloatField()
    airTemperatureMax = models.FloatField()
    airTemperatureMaxTime = models.TimeField()
    airTemperatureMin = models.FloatField()
    airTemperatureMinTime = models.TimeField()
    airHumidityAvg = models.FloatField()
    airHumidityMax = models.FloatField()
    airHumidityMaxTime = models.TimeField()
    airHumidityMin = models.FloatField()
    airHumidityMinTime = models.TimeField()
    rainAvg = models.FloatField()
    rainMax = models.FloatField()
    rainMaxTime = models.TimeField()
    rainMin = models.FloatField()
    rainMinTime = models.TimeField()
    rainTot = models.FloatField()
    gustOfWindAvg = models.FloatField()
    gustOfWindMax = models.FloatField()
    gustOfWindMaxTime = models.TimeField()
    gustOfWindMin = models.FloatField()
    gustOfWindMinTime = models.TimeField()
    dewPointAvg = models.FloatField()
    dewPointMax = models.FloatField()
    dewPointMaxTime = models.TimeField()
    dewPointMin = models.FloatField()
    dewPointMinTime = models.TimeField()
    ETTot = models.FloatField()
    groundTemperatureAvg = models.FloatField()
    groundTemperatureMax = models.FloatField()
    groundTemperatureMaxTime = models.TimeField()
    groundTemperatureMin = models.FloatField()
    groundTemperatureMinTime = models.TimeField()
    groundHumidityAvg = models.FloatField()
    groundHumidityMax = models.FloatField()
    groundHumidityMaxTime = models.TimeField()
    groundHumidityMin = models.FloatField()
    groundHumidityMinTime = models.TimeField()

    def __str__(self):
        return self.date.strftime('%d/%m/%Y')
