# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CompanyProfile
from users.models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_company_profile(sender, instance, created, **kwargs):
    if created and instance.is_seller:  # Only create CompanyProfile if user is a seller
        CompanyProfile.objects.create(user=instance)
