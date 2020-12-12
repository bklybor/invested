from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import AnonymousUser
from home.models import User

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home(request):
    if isinstance(request, User):
        if request.user.is_authenitcated:
            if request.user.is_client:
                # return the client view of the table app
                pass
            elif request.user.is_broker:
                # return the broker view of teh table app
                pass
    return render(request, 'table/home.html')