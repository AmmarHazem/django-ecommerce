from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length = 30)
    class Meta:
        model = User
        fields = ('email', 'full_name', 'password1', 'password2',)