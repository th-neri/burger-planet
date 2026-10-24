from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import (Collection, Product, ProductImage, Customer, Address, OrderItem, Cart, CartItem, Order, OrderItem)
from .serializers import (CollectionSerializer, ProductSerializer, ProductImageSerializer, CustomerSerializer, AddressSerializer,
                           CartSerializer, CartItemSerializer, AddItemToCartSerializer, UpdateCartItemSerializer)
from .permissions import IsAdminOrReadOnly
from .pagination import DefaultPagination
from .filters import ProductFilter

# COLLECTION CLASSES
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('products')).all().order_by('id')
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error: Collection cannot be deleted because it is associated with product(s).'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super.destroy(request, *args, **kwargs)


# PRODUCT VIEW CLASSES
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter 
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'last_update']
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error: Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]

    # to return only the images of the selected product
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    # to pass extra data from here to the ProductImage serializer
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

# CUSTOMER VIEW CLASSES
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    # any customer can retrieve customer object but only authenticated or admin users are able to update
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

# ADDRESS VIEW CLASSES
class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = self.request.user
        # only admins can retrieve all the customers, regular customers can see only their own 
        if customer.is_staff:
            return Address.objects.all()
        customer = Customer.objects.get(user=self.request.user)
        return Address.objects.filter(user=customer)

    # to save the address with the user from the jwt token(the current logged user)
    def perform_create(self, serializer):
        customer = Customer.objects.get(user=self.request.user)
        serializer.save(user=customer)


# CART VIEW CLASSES
class CartViewSet(ModelViewSet):
    queryset = Cart.objects.prefetch_related('items__product')
    serializer_class = CartSerializer

    def get_permissions(self):
        if self.action == 'list':
            # only admins can see all the carts
            return [IsAdminUser()]
        # for creating (POST), retrieving one (GET detail) or deleting allow anyone
        return [AllowAny()]

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class CartItemViewSet(ModelViewSet):
    # added a filter to only get the products of the selected cart
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product').order_by('id')

    # extracting the cart ID from the URL and passing it to the serializer
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_serializer_class(self):
        self.http_method_names = ['get', 'post', 'patch', 'delete']

        if self.request.method == 'POST':
            return AddItemToCartSerializer
        elif self.request.method == 'PATCH':
            # to update is carts/<cart_id>/items/<product_id>
            return UpdateCartItemSerializer
        return CartItemSerializer


