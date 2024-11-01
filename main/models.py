import json
from django.db import models
import uuid
import bcrypt
from django.shortcuts import redirect
from .utils import gen_otp


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
        email = request.POST['email']
        password = request.POST['password']
        if bcrypt.checkpw(bytes(password, 'utf-8'), User.objects.get(email=email).password):
            user = User.objects.get(email=email)
            return user

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


# add logging later
class Log(models.Model):
    info = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=255, choices=[(
        'INFO', 'INFO'), ('ERROR', 'ERROR'), ('WARNING', 'WARNING')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pass


class Transaction(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    type = models.CharField(max_length=255, choices=[(
        "add", "add"), ("withdraw", "withdraw"), ("refund", "refund"), ("ticket", "ticket"), ("food", "food")], null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    otp = models.IntegerField(default=gen_otp(), unique=False, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)


class Theatre(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    seats = models.IntegerField(default=200)
    shows = models.JSONField(null=True, default=None)
    theatre_admin = models.ForeignKey(
        TheatreAdmin, on_delete=models.CASCADE, null=True)


class Movie(models.Model):
    id = models.UUIDField(default=uuid.uuid4,
                          editable=False, primary_key=True)
    movie_id = models.IntegerField(null=True, unique=False)
    title = models.CharField(max_length=255)
    popularity = models.FloatField()
    adult = models.BooleanField()
    overview = models.TextField()
    poster_path = models.CharField(max_length=255)
    release_date = models.DateField()
    vote_average = models.FloatField()
    backdrop_path = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    genre = models.JSONField(default=None, null=True)


class Food(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.CharField(max_length=255)


class Show(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    time = models.DateTimeField()
    price = models.IntegerField()


class Ticket(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_date = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(default=100)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, null=True)
    food_orders = models.JSONField(default=None, null=True)
    cancelled = models.BooleanField(default=False)
    show = models.ForeignKey(
        Show, on_delete=models.CASCADE, null=True, default=None)
    used = models.BooleanField(default=False)
    tickets = models.IntegerField(default=1)

    def get_orders(self):
        return json.loads(self.food_orders)

    def add_order(self, food, quantity):
        food = Food.objects.get(name=food)
        orders = self.get_orders()
        orders.append({food.name: quantity})
        self.food_orders = json.dumps(dict(orders))
        self.save()
        return food
