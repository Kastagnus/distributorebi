from django.urls import path
from .views import SellerListView, company_info_view

urlpatterns = [
    path('sellers/', SellerListView.as_view(), name='sellers'),
    path('dashboard/<int:company_id>/company_info/', company_info_view, name='company_info'),
]