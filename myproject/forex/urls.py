from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('individual/', views.individual_search, name='individual_search'),
    path('individual_result/', views.individual_result, name='individual_result'),
]
