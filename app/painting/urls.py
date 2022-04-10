from django.urls import path, include
from rest_framework.routers import DefaultRouter

from painting import views

# default router will automatically generate URLS for the viewset

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('supplies', views.SupplyViewSet)
router.register('paintings', views.PaintingViewSet)


app_name = 'painting'

urlpatterns = [  # all urls will be added here if we keep adding router
    path('', include(router.urls))
]
