from django.urls import path, include
from rest_framework.routers import DefaultRouter

from painting import views

# default router will automatically generate URLS for the viewset

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)


app_name = 'painting'

urlpatterns = [  # all urls will be added here
    path('', include(router.urls))
]
