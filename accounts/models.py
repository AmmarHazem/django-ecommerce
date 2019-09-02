from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta


from ECommerce.utils import unique_key

ACTIVATION_DAYS = getattr(settings, 'ACTIVATION_DAYS', 7)

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password = None, is_active = True, is_staff = False, is_admin = False):
        if not email:
            raise ValueError('Users must have an email.')
        if not password:
            raise ValueError('Users must have passwords')
        if not full_name:
            raise ValueError('Users must have a fullname')

        user = self.model(email = self.normalize_email(email))
        user.full_name = full_name
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.is_active = is_active
        user.save(using = self._db)
        return user

    def create_superuser(self, email, full_name, password):
        return self.create_user(email = email, full_name = full_name, password = password, is_staff = True, is_admin = True)

    def create_staff_user(self, email, full_name, password):
        return self.create_user(email = email, full_name = full_name, password = password, is_staff = True)

    def create_admin_user(self, email, full_name, password):
        return self.create_user(email = email, full_name = full_name, password = password, is_admin = True)


class User(AbstractBaseUser):
    use_in_migrations = True

    email = models.EmailField(max_length = 255, unique = True)
    is_active = models.BooleanField(default = True)
    staff = models.BooleanField(default = False)
    admin = models.BooleanField(default = False)
    time_stamp = models.DateTimeField(auto_now_add = True)
    full_name = models.CharField(max_length = 50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        if self.full_name:
            return self.full_name.split()[0]
        return self.email

    def has_perm(self, prem, obj = None):
        return True

    def has_module_perms(self, all_label):
        return True

    @property
    def is_staff(self):
        if self.admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin



class Guest(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.email


class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days = ACTIVATION_DAYS)
        end_range = now
        return self.filter(activated = False, forced_expired = False).filter(created__gte = start_range, created__lte = end_range)


class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using = self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        return self.model.objects.filter(Q(email = email) | Q(user__email = email))


class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    email = models.EmailField()
    key = models.CharField(max_length = 120, blank = True, null = True)
    activated = models.BooleanField(default = False)
    forced_expired = models.BooleanField(default = False)
    expires = models.IntegerField(default = 7) # 7 days
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk = self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            self.user.is_active = True
            self.user.save()
            self.activated = True
            self.save()
            return True
        return False


    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False


    def send_activation(self):
        if not self.activated and not self.forced_expired and self.key:
            base = getattr(settings, 'BASE_URL')
            path = reverse('accounts:confirm-email', kwargs = {'key' : self.key})
            context = {'email' : self.email, 'path' : path}
            txt_ = get_template('registration/emails/verify.txt').render(context)
            html_ = get_template('registration/emails/verify.html').render(context)
            subject = 'Verify Email for eCommmerce.'
            from_email = 'ammar.hazem0@gmail.com'
            recipient_list = [self.email]
            sent_email = send_mail(subject = subject, message = txt_, from_email = from_email, recipient_list = recipient_list, html_message = html_, fail_silently = False)
            return sent_email
        return False


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired and not instance.key:
        instance.key = unique_key(sender)

pre_save.connect(pre_save_email_activation, sender = EmailActivation)


def send_activation_email_to_user(sender, instance, created, *args, **kwargs):
    if created:
        activation = EmailActivation.objects.create(user = instance, email = instance.email)
        sent_email = activation.send_activation()


post_save.connect(send_activation_email_to_user, sender = User)
