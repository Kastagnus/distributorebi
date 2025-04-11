import os
from io import BytesIO
from regions.models import City
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from PIL import Image
from django.core.validators import FileExtensionValidator
from products.models import Category


class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='companyprofile')
    description = models.TextField(max_length=1500, blank=True, null=True)
    about_us = models.TextField(max_length=1500, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    catalog = models.FileField(upload_to='company_catalogues/',
                               blank=True,
                               null=True,
                               validators=[FileExtensionValidator(
                                   allowed_extensions=['pdf', 'docx', 'doc', 'xls', 'xlsx'])]
                               )
    presentation = models.FileField(upload_to='company_presentations/',
                                    blank=True,
                                    null=True,
                                    validators=[FileExtensionValidator(
                                        allowed_extensions=['pdf', 'docx', 'doc', 'xls', 'xlsx'])]

                                    )
    image = models.ImageField(
        upload_to='company_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    address = models.TextField(max_length=1500, blank=True, null=True, default='Georgia')
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    cities = models.ManyToManyField(City, related_name="companies")

    def __str__(self):
        return f'profile of {self.user.ltd_name}'
    def clean(self):
        """Validate image size before saving."""
        if self.image:
            max_size = 5 * 1024 * 1024  # 5 MB in bytes
            if self.image.size > max_size:
                raise ValidationError("Image file too large (max 5 MB).")
        if self.catalog:
            max_size = 20 * 1024 * 1024  # 20 MB in bytes
            if self.catalog.size > max_size:
                raise ValidationError("Catalog file too large (max 20 MB).")
        if self.presentation:
            max_size = 20 * 1024 * 1024  # 20 MB in bytes
            if self.presentation.size > max_size:
                raise ValidationError("Catalog file too large (max 20 MB).")


    def resize_image(self):
        """Resize the image to 150x150 pixels."""
        if not self.image:
            return

        # Open the uploaded image
        img = Image.open(self.image)

        # Convert to RGB if image is RGBA (e.g., PNG with transparency)
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Resize to 150x150
        img = img.resize((150, 150), Image.Resampling.LANCZOS)

        # Save the resized image to a BytesIO buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)  # Use JPEG for consistency
        buffer.seek(0)

        # Overwrite the image field with the resized version
        new_filename = f"company_{self.id}.jpg" if self.id else f"company_temp_{self.user.ltd_name}.jpg"
        self.image.save(new_filename, File(buffer), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        if self.pk:  # If the object already exists
            old_instance = CompanyProfile.objects.get(pk=self.pk)
            if old_instance.image and self.image != old_instance.image:
                # Delete the old image if a new one is uploaded
                if os.path.isfile(old_instance.image.path):
                    os.remove(old_instance.image.path)
        # self.clean()
        self.resize_image()
        super().save(*args, **kwargs)

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


class BranchContact(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='branch_contacts')
    contact_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.contact_name} - {self.region}"
# Create your models here.
