from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('homeWCategory/<str:pk>', views.homeWithCategory, name='homeW'),
    path('signup/', views.signup, name='signup'),
    path('search/', views.search, name='search'),
    path('logout2/', views.logout2, name='logout2'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('makebid', views.makeBid, name='makeBid'),
    path('stopBid', views.stopBid, name='stopBid'),
    path('buyNow', views.buyNow, name='buyNow'),
    path('addItem/', views.addItem, name='addItem'),
    path('addPackage/', views.package, name='package'),
    path('item/<str:pk>', views.item_detail, name='itemDetail'),
    path('item/<str:pk>/delete', views.remove_item, name='itemRemove'),
    path('activate/<uidb64>/<token>/',
        views.activate, name='activate'),
]
