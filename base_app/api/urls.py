from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.get_books),
    path('book/<str:id>/', views.get_book),
    path('books/by/', views.get_books_by),
    path('books/paginated/', views.get_paginated_books),
    path('books/add/', views.add_book),
    path('books/update/<str:id>/', views.update_book),
    path('books/delete/<str:id>/', views.delete_book),
    path('register-user/', views.register_user),
    path('login/', views.login),
    path('logout/', views.logout),
    path('users/', views.get_users),
    path('user/<str:id>/', views.get_user),
    path('users/delete/<str:id>/', views.delete_user),
    path('users/update/<str:id>/', views.update_user),
]
