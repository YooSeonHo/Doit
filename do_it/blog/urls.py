from django.urls import path
from django.urls.resolvers import URLPattern
from . import views


urlpatterns = [
    # path('',views.index),
    path('',views.PostList.as_view()),
    # path('<int:pk>/',views.single_post_page),
    path('<int:pk>/',views.PostDetail.as_view()),
    path('category/<str:slug>/', views.category_page),
]