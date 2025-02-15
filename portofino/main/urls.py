from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('crypto/<str:coin_id>/', views.crypto_details, name='crypto_details'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/add/<str:coin_id>/', views.add_to_portfolio, name='add_to_portfolio'),
    path('portfolio/remove/<str:coin_id>/', views.remove_from_portfolio, name='remove_from_portfolio'),
    path('portfolio/update/<str:coin_id>/', views.update_portfolio_quantity, name='update_portfolio_quantity'),
    path('api/search/', views.api_search, name='api_search'),
]
