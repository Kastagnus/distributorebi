from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
from users.models import CustomUser

class Category(models.Model):
    max_depth = 3
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               related_name='subcategories',
                               blank=True,
                               null=True
                               )
    level = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name

    def save(self, *args, **kwargs):
        if self.parent:
            if self.parent.level >= self.max_depth:
                raise ValidationError('Reached max depth of subcategories')
            self.level = self.level + 1
        super().save(*args,**kwargs)

class Product(models.Model):
    UNIT_CHOICES = [
        ('piece', _('Piece')),
        ('ml', _('Milliliter')),
        ('gram', _('Gram')),
        ('kg', _('Kilogram')),
    ]
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200,)
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='products'
    )
    subcategory = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='subproducts',
        blank=True,
        null=True
    )
    description = models.TextField(max_length=500, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')

    def __str__(self):
        return self.name


# Create your models here.
