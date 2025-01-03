import django_filters
from django.utils.timezone import now
from datetime import timedelta
from .models import Order

class OrderFilter(django_filters.FilterSet):
    date = django_filters.CharFilter(method='filter_by_date')

    class Meta:
        model = Order
        fields = ['date']

    def filter_by_date(self, queryset, name, value):
        """
        Filter orders based on date ranges.
        Allowed values:
        - 'today'
        - 'week'
        - 'month'
        - 'year'
        - 'hour'
        - Custom range (e.g., 'YYYY-MM-DD,YYYY-MM-DD').
        """
        if value == 'today':
            return queryset.filter(created_at__date=now().date())
        elif value == 'week':
            start_of_week = now().date() - timedelta(days=now().weekday())
            return queryset.filter(created_at__date__gte=start_of_week)
        elif value == 'month':
            return queryset.filter(created_at__year=now().year, created_at__month=now().month)
        elif value == 'year':
            return queryset.filter(created_at__year=now().year)
        elif value == 'hour':
            one_hour_ago = now() - timedelta(hours=1)
            return queryset.filter(created_at__gte=one_hour_ago)
        elif ',' in value:  # Custom range (e.g., 'YYYY-MM-DD,YYYY-MM-DD')
            start_date, end_date = value.split(',')
            return queryset.filter(created_at__date__range=[start_date, end_date])
        return queryset