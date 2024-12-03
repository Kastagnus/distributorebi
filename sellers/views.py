from django.views.generic import ListView
from products.models import Category
from users.models import CustomUser
from django.db.models.query import Q

class SellerListView(ListView):
    model = CustomUser
    template_name = 'sellers/distributors.html'
    context_object_name = 'sellers'
    paginate_by = 12

    def get_queryset(self):
        category_ids = self.request.GET.getlist('categories')  # Get selected category IDs
        search_term = self.request.GET.get('search', '')
        queryset = CustomUser.objects.filter(is_seller=True)
        if category_ids:
            # Include sellers with selected categories or products in those categories
            return CustomUser.objects.filter(
                Q(seller_categories__category_id__in=category_ids) |
                Q(products__category_id__in=category_ids)
            ).distinct()

        if search_term:
            queryset = queryset.filter(
                products__name__icontains=search_term
            ).distinct()

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prefetch subcategories and their children
        context['categories'] = Category.objects.filter(level=0).prefetch_related(
            'subcategories__subcategories'
        )
        context['selected_categories'] = self.request.GET.getlist('categories')

        return context

# Create your views here.
