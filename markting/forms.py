from django import forms
from .models import MarktingPrefrence


class MarktingPrefrenceForm(forms.ModelForm):
    subscribed = forms.BooleanField(label = 'Recieve markting Emails ?', required = False)
    class Meta:
        model = MarktingPrefrence
        fields = ('subscribed',)