from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.users_list_view, name='users_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle_active'),
]
