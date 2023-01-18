from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.start, name='start'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.SearchFormView.as_view(), name='search'),
]
