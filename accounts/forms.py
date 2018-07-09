from django import forms
from django.shortcuts import redirect
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Guest, EmailActivation
from .signals import user_logged_in


User = get_user_model()



class ReactivateEmail(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            link = reverse('accounts:signup')
            msg = ''' This Email does not exist, would you like to <a href="{link}">register</a> ? '''.format(link = link)
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class LoginForm(forms.Form):
    email = forms.EmailField(widget = forms.EmailInput(attrs = {'class' : 'form-control', 'placeholder' : 'Email'}))
    password = forms.CharField(widget = forms.PasswordInput(attrs = {'class' : 'form-control', 'placeholder' : 'Password'}))

    # override the default __init__() method of the Form class so we can 
    # access the request object on the form
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        cd  = self.cleaned_data

        # check if this user has confirmed his email address or not
        qs = User.objects.filter(email = cd['email'])
        if qs.exists():
            not_active = qs.filter(is_active = False)
            if not_active.exists():
                confirm_email = EmailActivation.objects.filter(email = cd['email'])
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    raise forms.ValidationError('Your Email has not been verified yet, Please check your Email')
                email_confirm_exists = EmailActivation.objects.email_exists(email = cd['email']).exists()
                if email_confirm_exists:
                    raise forms.ValidationError('Please go here to verify your Email')
                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError('This account is inactive')

        user = authenticate(request = request, username = cd['email'], password = cd['password'])
        if user is None:
            raise forms.ValidationError('Invalid credentials')
        login(request, user)
        self.user = user
        user_logged_in.send(user.__class__, instance = user, request = request)
        try:
            del request.session['user_email']
        except:
            pass
        return cd

    # def form_valid(self, form):
    #     request = self.request
    #     cd = form.cleaned_data
    #     user = authenticate(request = request, username = cd['email'], password = cd['password'])
    #     if user:
    #         login(request, user)
    #         user_logged_in.send(user.__class__, instance = user, request = request)
    #         return redirect('home')



class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ('email',)