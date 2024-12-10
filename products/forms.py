# forms.py
from django import forms
from .models import Product, Category

class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'unit', 'size']

    # Additional fields for category selection
    level_0_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(level=0),
        required=False,
        label="Category"
    )
    level_1_category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Subcategory"
    )
    level_2_category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Sub-subcategory"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Prepopulate fields based on the current instance of the product
            category = self.instance.category
            if category:
                # Traverse through the levels to find parent categories
                if category.level == 2:
                    # Level 2: Set level 2, level 1, and level 0 categories
                    self.fields['level_2_category'].initial = category
                    self.fields['level_2_category'].queryset = Category.objects.filter(parent=category.parent)
                    self.fields['level_1_category'].initial = category.parent
                    self.fields['level_1_category'].queryset = Category.objects.filter(parent=category.parent.parent)
                    self.fields['level_0_category'].initial = category.parent.parent
                    self.fields['level_0_category'].queryset = Category.objects.filter(level=0)
                elif category.level == 1:
                    # Level 1: Set level 1 and level 0 categories
                    self.fields['level_1_category'].initial = category
                    self.fields['level_1_category'].queryset = Category.objects.filter(parent=category.parent)
                    self.fields['level_0_category'].initial = category.parent
                    self.fields['level_0_category'].queryset = Category.objects.filter(level=0)
                elif category.level == 0:
                    # Level 0: Set level 0 category only
                    self.fields['level_0_category'].initial = category
                    self.fields['level_1_category'].queryset = Category.objects.filter(parent=category)

        if 'level_0_category' in self.data:
            try:
                category_id = int(self.data.get('level_0_category'))
                self.fields['level_1_category'].queryset = Category.objects.filter(parent_id=category_id)
            except (ValueError, TypeError):
                self.fields['level_1_category'].queryset = Category.objects.none()

        if 'level_1_category' in self.data:
            try:
                subcategory_id = int(self.data.get('level_1_category'))
                self.fields['level_2_category'].queryset = Category.objects.filter(parent_id=subcategory_id)
            except (ValueError, TypeError):
                self.fields['level_2_category'].queryset = Category.objects.none()

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

        if commit:
            product.save()

        return product
