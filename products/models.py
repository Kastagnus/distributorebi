from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
from users.models import CustomUser
import os
from io import BytesIO
from django.core.files import File
from PIL import Image

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
    image = models.ImageField(
        upload_to='category_images/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name

    def get_all_descendants(self):
        """Return a list of this category and all its descendants."""
        descendants = [self]
        subcategories = self.subcategories.all()
        for sub in subcategories:
            descendants.extend(sub.get_all_descendants())
        return descendants

    def clean(self):
        """Validate image size before saving."""
        if self.image:
            max_size = 5 * 1024 * 1024  # 5 MB in bytes
            if self.image.size > max_size:
                raise ValidationError("Image file too large (max 5 MB).")

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
        new_filename = f"category_{self.id}.jpg" if self.id else f"category_temp_{self.name}.jpg"
        self.image.save(new_filename, File(buffer), save=False)
        buffer.close()
    def save(self, *args, **kwargs):
        if self.parent:
            if self.parent.level >= self.max_depth:
                raise ValidationError('Reached max depth of subcategories')
            self.level = self.level + 1
            if self.parent.parent:
                if self.parent.level >= self.max_depth:
                    raise ValidationError('Reached max depth of subcategories')
                self.level = self.level + 1
        if self.pk:  # If the object already exists
            old_instance = Category.objects.get(pk=self.pk)
            if old_instance.image and self.image != old_instance.image:
                # Delete the old image if a new one is uploaded
                if os.path.isfile(old_instance.image.path):
                    os.remove(old_instance.image.path)

            # Validate image size
        self.clean()
        self.resize_image()
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
    description = models.TextField(max_length=500, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')
    size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True
    )
    def __str__(self):
        return self.name

    def clean(self):
        """Validate image size before saving."""
        if self.image:
            max_size = 5 * 1024 * 1024  # 5 MB in bytes
            if self.image.size > max_size:
                raise ValidationError("Image file too large (max 5 MB).")

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
        new_filename = f"product_{self.id}.jpg" if self.id else f"product_temp_{self.name}.jpg"
        self.image.save(new_filename, File(buffer), save=False)
        buffer.close()
    def save(self, *args, **kwargs):
        if self.pk:  # If the object already exists
            old_instance = Product.objects.get(pk=self.pk)
            if old_instance.image and self.image != old_instance.image:
                # Delete the old image if a new one is uploaded
                if os.path.isfile(old_instance.image.path):
                    os.remove(old_instance.image.path)
        self.clean()
        self.resize_image()
        super().save(*args, **kwargs)


# Create your models here.
