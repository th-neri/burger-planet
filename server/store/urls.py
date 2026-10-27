from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('collections', views.CollectionViewSet)
router.register('products', views.ProductViewSet, basename='products')
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('addresses', views.AddressViewSet, basename='addresses')
router.register('carts', views.CartViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
router.urls

# the cart lookup is the cart ID extracted from the ProductImageViewSet queryset and to access products/<product_id>/images
# that way, the admin can add images to the product
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

# the cart lookup is the cart ID extracted from the CartItemViewSet queryset and to access carts/<id>/items
# that way, the customer can add products to the cart
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls