import numpy as np

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError
from polymorphic.models import PolymorphicModel

from WineApp.models import Sensor, DailyData

# Create your models here.


class Wine(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Vintage(models.Model):
    year = models.IntegerField()
    value = models.FloatField(
        validators=[
            MaxValueValidator(5.0),
            MinValueValidator(1.0)
        ]
    )
    wine = models.ForeignKey(Wine, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('year', 'wine')

    def __str__(self):
        return str(self.year) + " - " + self.wine.name


class ClimaticIndex(PolymorphicModel):
    name = models.CharField(max_length=200, default="")
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_list(self, start_date, end_date):
        raise IntegrityError("Objects of type 'ClimaticIndex' shouldn't exist, only subclasses can exist.")


class MonthsAvgIndex(ClimaticIndex):
    start_month = models.IntegerField(
        validators=[
            MaxValueValidator(12),
            MinValueValidator(1)
        ]
    )
    end_month = models.IntegerField(
        validators=[
            MaxValueValidator(12),
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name_plural = 'Months Avg indices'

    def get_list(self, start_date, end_date):
        values_list = []
        start_year = start_date.year
        end_year = end_date.year
        query_set = DailyData.objects.filter(sensor=self.sensor, date__gte=start_date, date__lte=end_date)\
            .exclude(avg=None).filter(date__month__gte=self.start_month, date__month__lte=self.end_month)
        if query_set:
            for year in range(start_year, end_year + 1):
                year_set = query_set.filter(date__year=year)
                if year_set:
                    values_list.append(year_set.aggregate(models.Avg('avg')).get('avg__avg'))
                else:
                    values_list.append(np.nan)
            return values_list
        else:
            return None


class WinklerIndex(ClimaticIndex):

    def save(self, *args, **kwargs):
        queryset = WinklerIndex.objects.all()
        if not queryset:
            self.sensor = Sensor.objects.get(name="Temperatura aria")
            super(ClimaticIndex, self).save(*args, **kwargs)

    def get_list(self, start_date, end_date):
        values_list = []
        start_year = start_date.year
        end_year = end_date.year
        query_set = DailyData.objects.filter(sensor=self.sensor, date__gte=start_date, date__lte=end_date)\
            .exclude(avg=None).filter(date__month__gte=4, date__month__lte=10)
        if query_set:
            for year in range(start_year, end_year + 1):
                year_set = query_set.filter(date__year=year)
                if year_set:
                    wi_index = 0
                    for dayli_data in year_set:
                        if dayli_data.avg > 10:
                            wi_index += dayli_data.avg - 10
                    values_list.append(wi_index)
                else:
                    values_list.append(np.nan)
            return values_list
        else:
            return None


class HuglinIndex(ClimaticIndex):

    def save(self, *args, **kwargs):
        queryset = HuglinIndex.objects.all()
        if not queryset:
            self.sensor = Sensor.objects.get(name="Temperatura aria")
            super(ClimaticIndex, self).save(*args, **kwargs)

    def get_list(self, start_date, end_date):
        values_list = []
        start_year = start_date.year
        end_year = end_date.year
        query_set = DailyData.objects.filter(sensor=self.sensor, date__gte=start_date, date__lte=end_date). \
            exclude(avg=None, max=None).filter(date__month__gte=4, date__month__lte=9)
        if query_set:
            k = 1.03
            for year in range(start_year, end_year + 1):
                year_set = query_set.filter(date__year=year)
                if year_set:
                    hi_index = 0
                    for dayli_data in year_set:
                        hi_index += (dayli_data.avg + dayli_data.max - 20) / 2 * k
                    values_list.append(hi_index)
                else:
                    values_list.append(np.nan)
            return values_list
        else:
            return None
