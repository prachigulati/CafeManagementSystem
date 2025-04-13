from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('home/', views.home, name='home'),
    path('faqs/', views.faqs, name='faqs'),
    path('menu/', views.menu, name='menu'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('update_info/', views.update_info, name='update_info'),
    path('about/', views.about, name='about'),
    path('category/<str:food>', views.category, name='category'),
]
