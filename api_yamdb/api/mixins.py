from rest_framework import filters, mixins, viewsets

from .permission import IsAdminOrReadOnly


class CreateDestroyListGenericMixin(mixins.CreateModelMixin,
                                    mixins.DestroyModelMixin,
                                    mixins.ListModelMixin,
                                    viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CreateListDestroyUpdateRetrieveMixin(mixins.CreateModelMixin,
                                           mixins.ListModelMixin,
                                           mixins.DestroyModelMixin,
                                           mixins.UpdateModelMixin,
                                           mixins.RetrieveModelMixin,
                                           viewsets.GenericViewSet):

    permission_classes = (IsAdminOrReadOnly,)
