from django.shortcuts import render
from django.views.generic import View
from .forms import MessageForm
from django.core.mail import send_mail
from django.http import HttpResponse

class Contact(View):
    def get(self, request):
        form  = MessageForm()
        return render(request, 'contact/contact.html', {'form' : form})

    def post(self, request):
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            send_mail(
                message.name,
                message.message,
                'ammar.hazem0@gmail.com',
                [message.email],
                fail_silently=False,
            )
            return render(request, 'contact/contact.html', {'success' : True})
        if request.is_ajax():
            return HttpResponse(form.errors.as_json(), status = 400, content_type = 'application/json')
        return render(request, 'contact/contact.html', {'form' : form})
