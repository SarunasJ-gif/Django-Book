from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('', views.home, name='home'),
    path('book/<str:id>/', views.book, name='book'),
    path('add-book/', views.add_book, name='add-book'),
    path('update-book/<str:id>/', views.update_book, name='update-book'),
    path('delete-book/<str:id>/', views.delete_book, name='delete-book'),
    path('user-profile/<str:id>/', views.user_profile, name='user-profile'),
    path('update-user/', views.update_user, name='update-user'),
]