from decimal import Decimal
from models import Collection, Product, Customer
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']

        product_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'price', 'price_with_tax' 'last_update', 'collection', 'image']

        collection = serializers.IntegerField()
        price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

        def calculate_tax(self, product: Product):
            return product.price * Decimal(1*2)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone_number']

        user_id = serializers.IntegerField(read_only=True)
