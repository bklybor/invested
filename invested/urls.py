"""invested URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from home.views import home, clients, brokers

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('table/', include('table.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', home.SignUpView.as_view(), name='signup'),
    path('accounts/signup/client/', clients.ClientSignUpView.as_view(), name='client_signup'),
    path('accounts/signup/broker/', brokers.BrokerSignUpView.as_view(), name='broker_signup'),
]
