from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View, DetailView, FormView, UpdateView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.utils.safestring import mark_safe

from ECommerce.forms import SignUpForm
from .forms import LoginForm, GuestForm, ReactivateEmail
from .signals import user_logged_in
from .models import EmailActivation

User = get_user_model()

class UserUpdate(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/update_user.html'
    fields = ('full_name',)

    def dispatch(self, request, *args, **kwargs):
        # messages.success(request, 'Your credentials has been updated.')
        return super(UserUpdate, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('accounts:edit-credentials')


class AccountHome(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'
    def get_object(self):
        return self.request.user


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


class Login(FormView):
    form_class = LoginForm
    template_name = 'registration/login.html'

    def next(self):
        next = self.request.GET.get('next') or self.request.POST.get('next') or None
        print('get data', self.request.GET)
        if next is None:
            return reverse('home')
        return next

    # add the request object to the form's __init__() arguments so we can access it from the form
    def get_form_kwargs(self):
        kwargs = super(Login, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        next = self.next()
        return redirect(next)


# class Guest(View):
#     def post(self, request):
#         form  = GuestForm(request.POST)
#         if form.is_valid():
            
#         login_form = LoginForm(request)
#         return render(request, 'checkout.html', {'guest_form' : form, 'login_form' : login_form})

class Guest(FormView):
    form_class = GuestForm
    template_name = 'checkout.html'

    def form_invalid(self, form):
        return redirect('cart:checkout')

    def form_valid(self, form):
        request = self.request
        form.save()
        request.session['user_email'] = form.cleaned_data['email']
        return redirect('cart:checkout')

class ConfirmEmail(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmail
    def get(self, request, key):
        qs = EmailActivation.objects.filter(key = key)
        confirmable_qs = qs.confirmable()
        if confirmable_qs.count() == 1:
            obj = confirmable_qs.first()
            obj.activate()
            messages.success(request, 'Your email was verified. Now you can login.')
            return redirect('accounts:login')
        else:
            activated_qs = qs.filter(activated = True)
            if activated_qs.exists():
                reset_link = reverse('password:password_change')
                msg = ''' Your email is already confirmed. Do you need to <a href="{link}">reset your passwrod</a> '''.format(link = reset_link)
                messages.success(request, mark_safe(msg))
                return redirect('accounts:login')
        context = {'form' : self.get_form()}
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, key):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = 'Activation link sent, please check your email'
        messages.success(self.request, msg)
        email = form.cleaned_data['email']
        email_activation_obj = EmailActivation.objects.email_exists(email = email).first()
        email_activation_obj.send_activation()
        return super(ConfirmEmail, self).form_valid(form)

    def form_invalid(self, form):
        context = {'form' : form}
        return render(self.request, 'registration/activation-error.html', context)