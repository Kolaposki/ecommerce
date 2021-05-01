from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.new_home, name='new_home'),
    path('wishlist/', views.wishlist, name='wishlist'),
]