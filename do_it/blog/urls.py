from django.urls import path
from django.urls.resolvers import URLPattern
from . import views


urlpatterns = [
    path('',views.index),
    path('<int:pk>/',views.single_post_page),
    
]