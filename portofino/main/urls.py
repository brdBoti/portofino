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
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/search/', views.search_users, name='search_users'),
    path('friends/request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('friend/<int:friend_id>/portfolio/', views.view_friend_portfolio, name='view_friend_portfolio'),
]
