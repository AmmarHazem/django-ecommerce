from django.shortcuts import render, redirect
from ECommerce.forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.views.generic import View

from .forms import LoginForm
from .signals import user_logged_in


class SignUp(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form' : form})

    def post(self, request):
        form  = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.full_name = form.cleaned_data['full_name']
            user.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request = request, username = email, password = password)
            if user:
                login(request, user)
                return redirect('home')
        return render(request, 'registration/signup.html', {'form' : form})


class Login(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'registration/login.html', {'form' : form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request = request, username = cd['username'], password = cd['password'])
            if user:
                login(request, user)
                user_logged_in.send(user.__class__, instance = user, request = request)
                return redirect('home')
        return render(request, 'registration/login.html', {'form' : form})


class Guest(View):
    def post(self, request):
        form  = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['user_email'] = form.cleaned_data['email']
            return redirect('cart:checkout')
        login_form = LoginForm()
        return render(request, 'checkout.html', {'guest_form' : form, 'login_form' : login_form})