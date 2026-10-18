from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import (Collection, Product, Customer, OrderItem)
from .serializers import (CollectionSerializer, ProductSerializer, CustomerSerializer)
from .permissions import IsAdminOrReadOnly
from .pagination import DefaultPagination
from .filters import ProductFilter

# COLLECTION CLASSES

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error: Collection cannot be deleted because it is associated with product(s).'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super.destroy(request, *args, **kwargs)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter 
    pagination_class = DefaultPagination
    search_fields = ['title', 'description', 'collection']
    ordering_fields = ['price', 'last_update']
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error: Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
