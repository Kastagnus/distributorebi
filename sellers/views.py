# views.py
import os

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView

from products.forms import CompanyProfileForm
from sellers.models import CompanyProfile, BranchContact
from users.models import CustomUser
from products.models import Category
from regions.models import City, Region


class SellerListView(ListView):
    model = CustomUser
    template_name = 'sellers/distributors.html'
    context_object_name = 'sellers'
    paginate_by = 10

    def get_queryset(self):
        category_ids = self.request.GET.getlist('categories')  # Get selected category IDs
        search_term = self.request.GET.get('search', '')
        region_ids = self.request.GET.getlist('regions')
        city_ids = self.request.GET.getlist('cities')
        # queryset = CustomUser.objects.filter(is_seller=True)
        queryset = CustomUser.objects.filter(is_seller=True).prefetch_related('companyprofile__cities__region')

        if category_ids:
            # Fetch all relevant category IDs including parents and children for selected categories
            selected_category_ids = set(map(int, category_ids))
            relevant_category_ids = set(selected_category_ids)

            for category_id in selected_category_ids:
                category = Category.objects.get(id=category_id)
                # Add parent and child categories if applicable
                if category.level == 2:
                    relevant_category_ids.add(category.parent.id)
                    relevant_category_ids.add(category.parent.parent.id)
                elif category.level == 1:
                    relevant_category_ids.add(category.parent.id)

            # Filter sellers by the relevant categories
            queryset = queryset.filter(
                Q(seller_categories__category_id__in=relevant_category_ids) |
                Q(products__category_id__in=relevant_category_ids)
            ).distinct().order_by('-id')
        if region_ids:
            # Filter by regions (sellers whose companyprofile.cities have the selected regions)
            queryset = queryset.filter(companyprofile__cities__region__id__in=region_ids)

        if city_ids:
            # Filter by cities
            queryset = queryset.filter(companyprofile__cities__id__in=city_ids)
        if search_term:
            queryset = queryset.filter(
                products__name__icontains=search_term
            ).distinct().order_by('-id')

        return queryset.distinct().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch top-level categories and prefetch related subcategories
        categories = Category.objects.filter(level=0).prefetch_related('subcategories__subcategories')
        regions = Region.objects.prefetch_related('cities')
        context['categories'] = categories
        context['selected_categories'] = self.request.GET.getlist('categories')
        context['regions'] = regions
        context['selected_regions'] = self.request.GET.getlist('regions')
        context['selected_cities'] = self.request.GET.getlist('cities')
        return context

# # Create your views here.

@login_required
def edit_company_profile(request, company_id):
    user = get_object_or_404(CustomUser, id=company_id)
    company_info = get_object_or_404(CompanyProfile, user=user)

    if request.user != user:
        return redirect('some_error_page')

    if request.method == 'POST':
        # Update user fields
        user.brand_name = request.POST.get('brand_name')
        user.ltd_name = request.POST.get('ltd_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number') if request.POST.get('phone_number') else None
        user.save()

        # Update company profile fields
        company_info.about_us = request.POST.get('about_us')
        company_info.address = request.POST.get('address')
        company_info.website = request.POST.get('website')
        company_info.facebook = request.POST.get('facebook')
        company_info.twitter = request.POST.get('twitter')
        company_info.linkedin = request.POST.get('linkedin')

        # Update cities from POST
        city_ids = request.POST.getlist('cities')
        city_ids = [int(cid) for cid in city_ids[0].split(',') if cid]
        company_info.cities.set(city_ids)
        # Handle branch contacts
        company_info.branch_contacts.all().delete()
        branch_counter = 1
        while f'branch_name_{branch_counter}' in request.POST:
            name = request.POST.get(f'branch_name_{branch_counter}')
            position = request.POST.get(f'branch_position_{branch_counter}')
            phone = request.POST.get(f'branch_phone_{branch_counter}')
            region = request.POST.get(f'branch_region_{branch_counter}')
            if name and position and phone and region:
                BranchContact.objects.create(
                    company=company_info,
                    contact_name=name,
                    position=position,
                    phone_number=phone,
                    region=region
                )
            branch_counter += 1
        if 'catalogue' in request.FILES:
            if company_info.catalog:
                if os.path.isfile(company_info.catalog.path):
                    os.remove(company_info.catalog.path)
            company_info.catalog = request.FILES['catalogue']
        elif request.POST.get('remove_catalogue'):
            if company_info.catalog:
                if os.path.isfile(company_info.catalog.path):
                    os.remove(company_info.catalog.path)
                company_info.catalog = None

            # Handle presentation file
        if 'presentation' in request.FILES:
            if company_info.presentation:
                if os.path.isfile(company_info.presentation.path):
                    os.remove(company_info.presentation.path)
            company_info.presentation = request.FILES['presentation']
        elif request.POST.get('remove_presentation'):
            if company_info.presentation:
                if os.path.isfile(company_info.presentation.path):
                    os.remove(company_info.presentation.path)
                company_info.presentation = None
        company_info.save()
        return redirect('dashboard', company_id=company_id)

    # Fetch all regions with their cities for the template
    regions = Region.objects.prefetch_related('cities').all()
    # pass

    return render(request, 'sellers/edit_info.html', {
        'user': user,
        'company_info': company_info,
        'regions': regions,
    })