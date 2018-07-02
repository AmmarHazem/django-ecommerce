from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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
        user.active = is_active
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
    active = models.BooleanField(default = True)
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
        return self.staff

    @property
    def is_admin(self):
        return self.admin

