from decimal import Decimal
from django.db import models
from .models import Collection, Product, ProductImage, Customer, Address, Cart, CartItem, Order, OrderItem
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']

    product_count = serializers.IntegerField(read_only=True)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    # to extract the product_id(product_pk) from the ProductImageViewSet serializer context, create and return the new image
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'price', 'price_with_tax', 'collection', 'images']

    collection = serializers.StringRelatedField()
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    images = ProductImageSerializer(many=True, read_only=True)

    def calculate_tax(self, product: Product):
        return round(product.price * Decimal(1.1), 2)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'username', 'phone_number']

    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username')
    phone_number = serializers.CharField(source='user.phone_number')

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'address', 'city', 'description', 'zipcode', 'is_default']
        read_only_fields = ['user']

#to retrieve only basic information of the product table
class SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'collection', 'image']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    product = SimpleSerializer()
    total_price = serializers.SerializerMethodField()

    # this to calculate the total price of every product added to the cart
    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.price

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'placed_at']

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    placed_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S') # to custom the placed_at so it looks cleaner
    total = serializers.SerializerMethodField()

    # to calculate the total of every product added to the cart
    def get_total(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

class AddItemToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    product_id = serializers.IntegerField()

    # to check if the product with the given ID exists, if not then it will raise a message
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
