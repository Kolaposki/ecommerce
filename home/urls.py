from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.new_home, name='new_home'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist_actions_ajax/', views.wishlist_actions_ajax, name='wishlist_actions_ajax'),
]