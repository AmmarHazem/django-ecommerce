from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from accounts.signals import user_logged_in
from accounts.models import User
from .signals import object_viewed_signal
from .utils import get_client_ip


class ObjectViewedQuerySet(models.query.QuerySet):
    def by_model(self, model_class):
        c_type = ContentType.objects.get_for_model(model_class)
        return self.filter(content_type = c_type)


class ObjectViewedManager(models.Manager):
    def get_query_set(self):
        return ObjectViewedQuerySet(self.model, using = self._db)

    def by_model(self, model_class):
        return self.get_query_set().by_model(model_class)


class ObjectViewed(models.Model):
    user = models.ForeignKey(User, null = True, blank = True, on_delete = models.SET_NULL)
    content_type = models.ForeignKey(ContentType, null = True, on_delete = models.SET_NULL)
    object_id = models.PositiveIntegerField()
    ip_address = models.CharField(max_length = 120, blank = True)
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add = True)

    objects = ObjectViewedManager()

    def __str__(self):
        return '%s viewd at: %s' % (self.content_object, self.timestamp)

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = 'Object Viewed'
        verbose_name_plural = 'Objects Viewed'


def object_viewed_reciever(sender, instance, request, *args, **kwargs):
    print('OBJECT VIEWD')
    c_type = ContentType.objects.get_for_model(sender) # = instance.__calss__
    ip_address = get_client_ip(request)
    user = None
    if request.user.is_authenticated:
        user = request.user
    
    new_view_instance = ObjectViewed.objects.create(user = user, content_type=c_type, object_id=instance.id, ip_address=ip_address)

object_viewed_signal.connect(object_viewed_reciever)


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    ip_address = models.CharField(max_length = 120, blank = True)
    session_key = models.CharField(max_length = 100, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True)
    active = models.BooleanField(default = True)
    ended = models.BooleanField(default = False)

    def __str__(self):
        return str(self.user) + ': ' + self.session_key

    def end_session(self):
        try:
            print('DELETEING SESSION: {}'.format(self.session_key))
            Session.objects.get(pk = self.session_key).delete()
            print('SESSION ENDED')
            self.active = False
            self.ended = True
            self.save()
        except:
            print('Did not delete the user session')


def post_save_session(sender, instance, created, *args, **kwargs):
    if created:
        qs = UserSession.objects.filter(user = instance.user).exclude(id = instance.id)
        if qs.exists:
            for s in qs:
                s.end_session()

post_save.connect(post_save_session, sender = UserSession)


def user_loggedin_reciever(sender, instance, request, *args, **kwargs):
    ip = get_client_ip(request)
    UserSession.objects.create(user = instance, ip_address = ip, session_key = request.session.session_key)

user_logged_in.connect(user_loggedin_reciever)