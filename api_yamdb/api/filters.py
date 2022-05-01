from django_filters import CharFilter, FilterSet, NumberFilter
from titles.models import Title


class TitleFilter(FilterSet):
    """Фильтры для произведений."""

    genre = CharFilter(
        field_name='genre__slug',
    )
    category = CharFilter(
        field_name='category__slug',
    )
    name = CharFilter(
        field_name='name',
        lookup_expr='contains'
    )
    year = NumberFilter(
        field_name='year',
    )

    class Meta:
        model = Title
        fields = '__all__'
