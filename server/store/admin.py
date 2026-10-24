from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

class CollectionFilter(admin.SimpleListFilter):
    title = 'collection'
    parameter_name = 'collection'

    # fetch all the collections
    def lookups(self, request, model_admin):
        return [(collection.id, collection.title) for collection in models.Collection.objects.all()]

    # if the admin selects a collection from the filter sidebar
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(collection_id=self.value())
        return queryset

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    ordering = ['title']
    search_fields = ['title']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
                   'collection_id': str(collection.id)
               }))
        return format_html('<a href="{}">{}</a>', url, collection.product_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']
    extra = 1  # shows 1 empty upload row by default so i can add more than one image

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" style="height: auto; border-radius: 4px;" />', obj.image.url)
        return '-'

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'price', 'collection_title']
    list_filter = [CollectionFilter]
    ordering = ['title']
    search_fields = ['title']
    list_editable = ['price']
    list_per_page = 15
    inlines = [ProductImageInline]

    def collection_title(self, product):
        return product.collection.title

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'user__email', 'user__phone_number']
    list_select_related = ['user']
    search_fields = ['user__email', 'user__username', 'phone_number']
    ordering = ['user__username']
    list_per_page = 15

    #to count the quantity of orders of every customer and provide the link to the customer page
    #where you can see every order of a specific customer
    @admin.display(ordering='total_orders')
    def total_orders(self, customer):
        url = (reverse('admin:store_order_changelist')
               + '?'
               + urlencode({
                   'customer_id': str(customer.id)
               }))
        return format_html('<a href="{}">{}</a>', url, customer.total_orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_orders=Count('orders')
        )

class OrderInLine(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    extra = 0
    readonly_fields = ['price']
    min_num = 1
    max_num = 10

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'placed_at', 'total_price', 'is_paid']
    list_editable = ['is_paid']
    list_filter = ['is_paid', 'placed_at']
    inlines = [OrderInLine]

@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'address', 'city', 'description', 'zipcode', 'is_default']
    list_select_related = ['user']
    list_editable = ['is_default']
    ordering = ['id', 'user']

@admin.register(models.CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']   