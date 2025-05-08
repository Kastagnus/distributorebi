from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    name_en = models.CharField(max_length=255, unique=True, blank=True, null=True)
    name_ru = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    name_en = models.CharField(max_length=255, unique=True, blank=True, null=True)
    name_ru = models.CharField(max_length=255, unique=True, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name} ({self.region.name})"