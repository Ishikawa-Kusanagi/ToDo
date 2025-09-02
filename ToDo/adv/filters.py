from django_filters import rest_framework as filters

from .models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    created_at = filters.DateFromToRangeFilter()
    status = filters.CharFilter()

    class Meta:
        model = Advertisement
        fields = {
            'status': ['exact'],
            'title': ['icontains'],
            'created_at': ['date__gre', 'date_lte'],
            'creator': ['exact']
        }
