from django.urls import path

from products.views import dashboard
from .views import SellerListView, edit_company_profile

urlpatterns = [
    path('sellers/', SellerListView.as_view(), name='sellers'),
    path('dashboard/<int:company_id>', edit_company_profile, name='edit_company_profile'),
]