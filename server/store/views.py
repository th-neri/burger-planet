from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import (Collection, Product, ProductImage, Customer, Address, OrderItem, Cart, CartItem, Order, OrderItem)
from .serializers import (CollectionSerializer, ProductSerializer, ProductImageSerializer, CustomerSerializer, UpdateCustomerSerializer, 
                          AddressSerializer, CartSerializer, CartItemSerializer, AddItemToCartSerializer, UpdateCartItemSerializer, 
                          OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer)
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
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateCustomerSerializer
        return CustomerSerializer

    def get_permissions(self):
        # admins can do anything
        if self.request.user and self.request.user.is_staff:
            return [IsAdminUser()]

        # only for regular users
        if self.request.method in ['GET', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    # only admins can retrieve all the customers, regular customers can see only their own 
    def get_queryset(self):
        user = self.request.user

        # admins can retrieve all users, regular customer can retrieve only their own
        if user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=user)

    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        customer, _ = Customer.objects.get_or_create(user=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(CustomerSerializer(customer).data)

    # any customer can retrieve customer object but only authenticated or admin users are able to update
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

# ADDRESS VIEW CLASSES
class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    # only admins can retrieve all the addresses, regular customers can see only their own 
    def get_queryset(self):
        customer = self.request.user
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

# ORDER VIEW CLASSES
class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user

        # only return all the orders if the user is admin
        if user.is_staff:
            return Order.objects.all()
        # and if the user is not admin then it only returns the orders of this user
        return Order.objects.filter(user_id=user.id)

    # only able to update or delete if admin
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    # implemented a create method from scratch using the current user ID to create an order
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(request.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
