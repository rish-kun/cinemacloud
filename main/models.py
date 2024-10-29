from django.db import models
import uuid
import bcrypt
from django.shortcuts import redirect
# Create your models here.


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.BinaryField(max_length=255)
    name = models.CharField(max_length=255)
    tickets = models.JSONField(default=None, null=True)
    money = models.IntegerField(default=1000)
    transaction_history = models.JSONField(default=None, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email_verified = models.BooleanField(default=False)

    def get_current_ticket(self):
        pass

    def authenticate(self, request):
        pass

    @staticmethod
    def get_user(request, path):
        try:
            request.COOKIES['user-identity']
        except KeyError:
            return redirect(f'main:{path}')
        try:
            user = User.objects.get(uuid=request.COOKIES['user-identity'])
        except User.objects.DoesNotExist:
            resp = redirect(f'main:{path}')
            resp.delete_cookie('user-identity')
            return resp
        else:
            return None


class SuperAdmin(models.Model):
    pass


class TheatreAdmin(models.Model):
    pass
