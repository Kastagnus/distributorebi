from django.urls import path
from .views import SellerListView

urlpatterns = [
    path('sellers/', SellerListView.as_view(), name='sellers')
]