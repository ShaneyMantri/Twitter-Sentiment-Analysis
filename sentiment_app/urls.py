from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="TweetHome"),
    path('keyword_search/', views.keyword_search, name="Keywordsearch"),

]
