"""
URL configuration for Postman_api_event project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Postman_api_event import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login/', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('demo/', views.demo),
    path('profile/', views.profile),
    path('stock/search/', views.stock_search, name='stock_search'),
    path('stock/search/<symboltoken>/', views.stock_search_detail, name='stock_search_detail'), 
    path('deleteStockINwatchList/<symboltoken>', views.deleteStockINwatchList, name='deleteStockINwatchList'), 
    path('addWatchlist', views.addWatchlist, name='addWatchlist'),
    path('getStockLTP', views.getStockLTP, name='getStockLTP'),
    path('getWatchList', views.getWatchList, name='getWatchList'),
    path('buyStock', views.buyStock, name='buyStock'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('orderbook/', views.get_order_book, name='orderbook'),

]
