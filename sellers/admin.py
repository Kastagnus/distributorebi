from django.contrib import admin
from .models import CompanyProfile, SellerCategory
admin.site.register(CompanyProfile)


# admin.site.register(SellerCategory)

@admin.register(SellerCategory)
class SellerCategoryAdmin(admin.ModelAdmin):
    pass
# Register your models here.
