from django.urls import path

from user import views


# which app create URL from
app_name = 'user'

# will be handy when we use the reverse fucntion
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
]
