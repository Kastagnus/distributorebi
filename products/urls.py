from django.urls import path
from .views import company_dashboard

urlpatterns = [
    # Company Dashboard
    path('dashboard/<int:company_id>/', company_dashboard, name='dashboard'),

    # Company Actions (for authenticated users only)
    # path('company/<int:company_id>/modify/', views.modify_company, name='modify_company'),
    # path('company/<int:company_id>/delete/', views.delete_company, name='delete_company'),
    #
    # # Product Actions
    # path('product/add/', views.add_product, name='add_product'),  # Add product
    # path('product/<int:product_id>/modify/', views.modify_product, name='modify_product'),  # Modify product
    # path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),  # Delete product
]