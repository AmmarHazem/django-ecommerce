from django.shortcuts import redirect
from django.views.generic import UpdateView, View
from django.conf import settings
from django.http import HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from .models import MarktingPrefrence
from .forms import MarktingPrefrenceForm
from .utils import Mailchimp
from .mixins import CSRFExemptMixin

MAILCHIMP_API_KEY           = getattr(settings, 'MAILCHIMP_API_KEY')
MAILCHIMP_DATA_CENTER       = getattr(settings, 'MAILCHIMP_DATA_CENTER')
MAILCHIMP_EMAIL_LIST_ID     = getattr(settings, 'MAILCHIMP_EMAIL_LIST_ID')


class MarktingPrefrenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarktingPrefrenceForm
    template_name = 'markting/email.html'
    success_url = '/settings/emails/'
    success_message = 'Your email prefrence is updated successfuly'

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect('/accounts/login/?next={next}'.format(next = self.success_url))
        return super(MarktingPrefrenceUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return self.request.user.marktingprefrence


class MailchimpWebhook(CSRFExemptMixin, View):
    def post(self, request):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == MAILCHIMP_EMAIL_LIST_ID:
            hooktype = data.get('type')
            email = data.get('data[email]')
            status, response = Mailchimp().check_sub_status(email)
            sub_status = response.get('status')
            is_subbed, mailchimp_subbed = None, None
            if sub_status == 'subscribed':
                is_subbed,  mailchimp_subbed = True, True
            elif sub_status == 'unsubscribed':
                is_subbed,  mailchimp_subbed = False, False
            if is_subbed and mailchimp_subbed is not None:
                mp = MarktingPrefrence.objects.get(user__email = email)
                mp.subscribed = is_subbed
                mp.mailchimp_subscribed = mailchimp_subbed
                mp.mailchimp_msg = str(data)
                mp.save()
            return HttpResponse('Thank you', status = 200)

