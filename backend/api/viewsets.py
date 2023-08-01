from rest_framework import mixins
from .pagination import LimitPagesPagination
from rest_framework import viewsets


class CreateReadViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    pagination_class = LimitPagesPagination
