from rest_framework import mixins
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets

from .permissions import IsAdminOrReadOnly


class CreateDestroyReadViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
