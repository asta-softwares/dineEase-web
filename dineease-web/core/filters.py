import django_filters
from django.db.models import Q
from .models import Restaurant

class RestaurantFilter(django_filters.FilterSet):
    # Custom search across name, location, and category
    search = django_filters.CharFilter(method='search_filter', label='Search')

    # Old filters
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name')
    categories = django_filters.CharFilter(method='filter_categories', label='Categories')
    service_type = django_filters.CharFilter(method='filter_service_type', label='Service Type')  # Use CharFilter instead of ChoiceFilter

    class Meta:
        model = Restaurant
        fields = ['name', 'categories', 'service_type']

    def search_filter(self, queryset, name, value):
        """
        Custom filter for searching across name, location, and category.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(location__icontains=value) |
            Q(categories__name__icontains=value)
        ).distinct()

    def filter_categories(self, queryset, name, value):
        """
        Filter by categories, supporting multiple category IDs separated by commas.
        """
        try:
            category_ids = [int(cat_id) for cat_id in value.split(',')]
            return queryset.filter(categories__id__in=category_ids).distinct()
        except ValueError:
            return queryset.none()
        
    def filter_service_type(self, queryset, name, value):
        """
        Filter restaurants by service type. If 'both' is specified,
        include restaurants with 'dine-in' or 'takeout'.
        """
        if value == 'both':
            return queryset.filter(
                Q(service_type='dine-in') | Q(service_type='takeout') | Q(service_type='both')
            )
        return queryset.filter(service_type=value)
