from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import Register
from .forms import EmailAuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView

class RegisterView(CreateView):
    form_class = Register
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')