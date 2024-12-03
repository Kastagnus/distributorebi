from django.contrib import admin
from .models import Product, Category
admin.site.register(Product)
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)