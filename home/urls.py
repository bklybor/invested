from django.urls import include, path

from home.views import home

app_name = 'home'

urlpatterns = [
    path('', home.home, name= 'home'),
    
]