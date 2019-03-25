from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'customer'

urlpatterns = [
    url(r'^$', views.FoodCategoryListView.as_view(), name='category_menu'),
    url(r'^(?P<pk>[-\w]+)/$', views.FoodCategoryDetailView.as_view(), name='food_menu'),
    url(r'^orders', views.OrderListView.as_view(), name='orders'),
]

