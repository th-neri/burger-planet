from decimal import Decimal
from django.db import models
from .models import Collection, Product, Customer, Address
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']

    product_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'price', 'price_with_tax', 'collection', 'image']

    collection = serializers.StringRelatedField()
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

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

