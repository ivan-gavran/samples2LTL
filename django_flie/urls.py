from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/learn/', views.learn, name='learn'),
    path('ajax/result/', views.result, name='result',),
    path('syntax', views.syntax, name='syntax')
]
