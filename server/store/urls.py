from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('collections', views.CollectionViewSet)
router.register('products', views.ProductViewSet, basename='products')
router.register('customers', views.CustomerViewSet)
router.register('addresses', views.AddressViewSet, basename='addresses')
router.register('carts', views.CartViewSet)

# the cart lookup is the cart ID extracted from the CartItemViewSet queryset and to access carts/<id>/items
# that way, the customer can add products to the cart
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + carts_router.urls