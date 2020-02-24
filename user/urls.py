from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout2/', views.logout2, name='logout2'),
    path('activate/<uidb64>/<token>/',
        views.activate, name='activate'),
]
