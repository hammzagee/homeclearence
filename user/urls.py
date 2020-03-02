from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout2/', views.logout2, name='logout2'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('makebid', views.makeBid, name='makeBid'),
    path('stopBid', views.stopBid, name='stopBid'),
    path('buyNow', views.buyNow, name='buyNow'),
    path('addItem/', views.addItem, name='addItem'),
    path('item/<str:pk>', views.item_detail, name='itemDetail'),
    path('activate/<uidb64>/<token>/',
        views.activate, name='activate'),
]
