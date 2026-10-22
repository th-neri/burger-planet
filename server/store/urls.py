from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('collections', views.CollectionViewSet)
router.register('products', views.ProductViewSet, basename='products')
router.register('customers', views.CustomerViewSet)
router.register('addresses', views.AddressViewSet, basename='addresses')

urlpatterns = router.urls