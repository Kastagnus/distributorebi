# forms.py
from django import forms

from sellers.models import CompanyProfile
from .models import Product, Category
from django_select2.forms import Select2MultipleWidget
from regions.models import City


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']
        widgets = {
            'cities': Select2MultipleWidget(attrs={'data-placeholder': 'Select cities'})
        }

#
# class ProductCreateForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'unit', 'size']
#
#     # Additional fields for category selection
#     level_0_category = forms.ModelChoiceField(
#         queryset=Category.objects.filter(level=0),
#         required=False,
#         label="Category"
#     )
#     level_1_category = forms.ModelChoiceField(
#         queryset=Category.objects.none(),
#         required=False,
#         label="Subcategory"
#     )
#     level_2_category = forms.ModelChoiceField(
#         queryset=Category.objects.none(),
#         required=False,
#         label="Sub-subcategory"
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         if self.instance and self.instance.pk:
#             # Prepopulate fields based on the current instance of the product
#             category = self.instance.category
#             if category:
#                 # Traverse through the levels to find parent categories
#                 if category.level == 2:
#                     # Level 2: Set level 2, level 1, and level 0 categories
#                     self.fields['level_2_category'].initial = category
#                     self.fields['level_2_category'].queryset = Category.objects.filter(parent=category.parent)
#                     self.fields['level_1_category'].initial = category.parent
#                     self.fields['level_1_category'].queryset = Category.objects.filter(parent=category.parent.parent)
#                     self.fields['level_0_category'].initial = category.parent.parent
#                     self.fields['level_0_category'].queryset = Category.objects.filter(level=0)
#                 elif category.level == 1:
#                     # Level 1: Set level 1 and level 0 categories
#                     self.fields['level_1_category'].initial = category
#                     self.fields['level_1_category'].queryset = Category.objects.filter(parent=category.parent)
#                     self.fields['level_0_category'].initial = category.parent
#                     self.fields['level_0_category'].queryset = Category.objects.filter(level=0)
#                 elif category.level == 0:
#                     # Level 0: Set level 0 category only
#                     self.fields['level_0_category'].initial = category
#                     self.fields['level_1_category'].queryset = Category.objects.filter(parent=category)
#
#         if 'level_0_category' in self.data:
#             try:
#                 category_id = int(self.data.get('level_0_category'))
#                 self.fields['level_1_category'].queryset = Category.objects.filter(parent_id=category_id)
#             except (ValueError, TypeError):
#                 self.fields['level_1_category'].queryset = Category.objects.none()
#
#         if 'level_1_category' in self.data:
#             try:
#                 subcategory_id = int(self.data.get('level_1_category'))
#                 self.fields['level_2_category'].queryset = Category.objects.filter(parent_id=subcategory_id)
#             except (ValueError, TypeError):
#                 self.fields['level_2_category'].queryset = Category.objects.none()
#
#     def save(self, commit=True):
#         product = super().save(commit=False)
#         level_2_category = self.cleaned_data.get('level_2_category')
#         level_1_category = self.cleaned_data.get('level_1_category')
#         level_0_category = self.cleaned_data.get('level_0_category')
#
#         # Set the most specific category level selected
#         if level_2_category:
#             product.category = level_2_category
#         elif level_1_category:
#             product.category = level_1_category
#         elif level_0_category:
#             product.category = level_0_category
#
#         if commit:
#             product.save()
#
#         return product

from django import forms
from .models import Product, Category

class ProductCreateForm(forms.ModelForm):
    language = forms.ChoiceField(choices=[
        ('en', 'English'),
        ('ka', 'Georgian'),
        ('ru', 'Russian')
    ], label="Input Language")
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'unit', 'size', "image"]
        widgets = {"price": forms.NumberInput(attrs={'min': 0}),
                   "size": forms.NumberInput(attrs={'min': 0}),}


    # Additional fields for category selection
    level_0_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(level=0),
        required=False,
        label="Category"
    )
    level_1_category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Will be updated dynamically
        required=False,
        label="Subcategory"
    )
    level_2_category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Will be updated dynamically
        required=False,
        label="Sub-subcategory"
    )
    image = forms.ImageField(
        required=False,
        label="Product Image"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Handle editing an existing product
        if self.instance and self.instance.pk and self.instance.category:
            category = self.instance.category
            if category.level == 2:
                self.fields['level_2_category'].initial = category
                self.fields['level_2_category'].queryset = Category.objects.filter(parent=category.parent)
                self.fields['level_1_category'].initial = category.parent
                self.fields['level_1_category'].queryset = Category.objects.filter(parent=category.parent.parent)
                self.fields['level_0_category'].initial = category.parent.parent
            elif category.level == 1:
                self.fields['level_1_category'].initial = category
                self.fields['level_1_category'].queryset = Category.objects.filter(parent=category.parent)
                self.fields['level_0_category'].initial = category.parent
            elif category.level == 0:
                self.fields['level_0_category'].initial = category
                self.fields['level_1_category'].queryset = Category.objects.filter(parent=category)

        # Handle form data (POST or GET with query params)
        if self.data.get('level_0_category'):
            try:
                category_id = int(self.data.get('level_0_category'))
                self.fields['level_1_category'].queryset = Category.objects.filter(parent_id=category_id)
            except (ValueError, TypeError):
                self.fields['level_1_category'].queryset = Category.objects.none()

        if self.data.get('level_1_category'):
            try:
                subcategory_id = int(self.data.get('level_1_category'))
                self.fields['level_2_category'].queryset = Category.objects.filter(parent_id=subcategory_id)
            except (ValueError, TypeError):
                self.fields['level_2_category'].queryset = Category.objects.none()

        # Set default querysets for new instances if no data is provided
        if not self.data and not (self.instance and self.instance.pk):
            # Optionally, set level_1_category queryset to all level 1 categories
            # self.fields['level_1_category'].queryset = Category.objects.filter(level=1)
            # Or keep it empty, relying on JavaScript to populate
            self.fields['level_1_category'].queryset = Category.objects.none()
            self.fields['level_2_category'].queryset = Category.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        level_0_category = cleaned_data.get('level_0_category')
        level_1_category = cleaned_data.get('level_1_category')
        level_2_category = cleaned_data.get('level_2_category')

        # Ensure a category is selected if any level is chosen
        if level_0_category and not level_1_category and not level_2_category:
            # Check if level_0_category has subcategories
            if Category.objects.filter(parent=level_0_category).exists():
                self.add_error('level_0_category', "Please select a subcategory or sub-subcategory if available.")
        elif level_1_category and not level_2_category:
            # Check if level_1_category has subcategories
            if Category.objects.filter(parent=level_1_category).exists():
                self.add_error('level_1_category', "Please select a sub-subcategory if available.")

        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)
        level_2_category = self.cleaned_data.get('level_2_category')
        level_1_category = self.cleaned_data.get('level_1_category')
        level_0_category = self.cleaned_data.get('level_0_category')

        # Set the most specific category level selected
        if level_2_category:
            product.category = level_2_category
        elif level_1_category:
            product.category = level_1_category
        elif level_0_category:
            product.category = level_0_category
        else:
            raise forms.ValidationError("Please select a valid category.")

        if commit:
            product.save()
        return product
