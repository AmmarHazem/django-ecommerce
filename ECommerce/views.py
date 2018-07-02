from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from cart.models import Cart


class Home(View):
    def get(self, request):
        cart, created = Cart.objects.new_or_get(request)
        request.session['n'] = cart.products.count()
        return render(request, 'base.html')

