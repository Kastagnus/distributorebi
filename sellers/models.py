from django.conf import settings
from django.db import models
from products.models import Category

class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                )
    description = models.TextField(max_length=1500, blank=True, null=True)
    about_us = models.TextField(max_length=1500, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    catalog = models.FileField(upload_to='catalogs/', blank=True, null=True)


    def __str__(self):
        return f'profile of {self.user.ltd_name}'


class SellerCategory(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_categories'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='seller_categories'
    )

    class Meta:
        unique_together = ('seller', 'category')  # Prevent duplicate entries
        verbose_name_plural = "Seller Categories"

    def __str__(self):
        return f"{self.seller.ltd_name} - {self.category.name}"

# Create your models here.
