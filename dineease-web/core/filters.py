import django_filters
from django.db.models import Q
from .models import Restaurant
from .constants import CANADA_PROVINCE_CHOICES

PROVINCE_MAP = {abbr: name.lower() for abbr, name in CANADA_PROVINCE_CHOICES}
PROVINCE_MAP.update({name.lower(): abbr for abbr, name in CANADA_PROVINCE_CHOICES})

class RestaurantFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Name')
    categories = django_filters.CharFilter(method='filter_categories', label='Categories')
    service_type = django_filters.CharFilter(method='filter_service_type', label='Service Type')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains', label='City')
    province = django_filters.CharFilter(method='filter_province', label='Province')

    class Meta:
        model = Restaurant
        fields = ['name', 'categories', 'service_type', 'city', 'province']

    def search_filter(self, queryset, name, value):
        """
        Custom filter for searching across name, location, category, and city.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(location__icontains=value) |
            Q(categories__name__icontains=value) |
            Q(city__icontains=value)
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
    
    def filter_province(self, queryset, name, value):
        """
        Filter by province, supporting both abbreviations and full names.
        """
        normalized_value = value.strip().lower()
        province_code = PROVINCE_MAP.get(normalized_value)
        if not province_code:
            return queryset.none()
        return queryset.filter(province=province_code)
