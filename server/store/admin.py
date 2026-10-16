from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    ordering = ['title']
    search_fields = ['title']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        url = (reverse('admin_store_product_changelist')
               + '?'
               + urlencode({
                   'collection_id': str(collection.id)
               }))
        return format_html('<a href="{}">{}</a>', url, collection.product_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('product')
        )

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'price', 'collection_title', 'thumbnail']
    ordering = ['title']
    search_fields = ['title']
    list_editable = ['price']
    list_per_page = 10

    def collection_title(self, product):
        return product.collection.title

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="object-fit: cover; border-radius: 5px;"/>', obj.image.url)
        return '-'

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    list_select_related = ['user']
    search_fields = ['user__email', 'user__username', 'phone_number']
    ordering = ['user__username']
    list_per_page = 10
