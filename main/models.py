import json
from django.db import models
import uuid
import bcrypt
from django.shortcuts import redirect
from .utils import gen_otp
from django.utils import timezone


class Wallet(models.Model):
    money = models.IntegerField(default=100)
    user_id = models.UUIDField(default=None, null=True)
    transaction_history = models.JSONField(null=True)


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.BinaryField(max_length=255)
    name = models.CharField(max_length=255)
    tickets = models.JSONField(default=None, null=True)
    # money = models.IntegerField(default=1000)
    # transaction_history = models.JSONField(default=None, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, default=None, null=True)
    email_verified = models.BooleanField(default=False)

    def create_wallet(self):
        self.wallet = Wallet.objects.create(user_id=self.uuid)

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


# add logging later
class Log(models.Model):
    info = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=255, choices=[(
        'INFO', 'INFO'), ('ERROR', 'ERROR'), ('WARNING', 'WARNING')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pass


class Theatre(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    seats = models.IntegerField(default=200)
    shows = models.JSONField(null=True, default=None)


class TheatreAdmin(models.Model):
    username = models.CharField(max_length=256, null=True)
    email = models.EmailField(unique=True, null=True)
    password = models.BinaryField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, default=None, null=True)
    theatre = models.ManyToManyField(
        Theatre, related_name="admin")


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
    to = models.ForeignKey(TheatreAdmin, on_delete=models.CASCADE, null=True)
    # to should be a dict of the format {"user_type":["normal", 'theatreadmin']}


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
    available_seats = models.IntegerField(default=100, null=False)
    is_active = models.BooleanField(default=True)

    def is_full(self):
        return self.available_seats <= 0

    def is_bookable(self):
        return self.is_active and not self.is_full() and self.time > timezone.now()

    def book_seats(self, num_seats):
        if self.available_seats >= num_seats:
            self.available_seats -= num_seats
            self.save()
            return True
        return False

    def release_seats(self, num_seats):
        self.available_seats += num_seats
        self.save()


class Ticket(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_date = models.DateTimeField(auto_now_add=True)
    price = models.BigIntegerField(default=100)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, null=True)
    food_orders = models.JSONField(default=None, null=True)
    cancelled = models.BooleanField(default=False)
    show = models.ForeignKey(
        Show, on_delete=models.CASCADE, null=True, default=None)
    used = models.BooleanField(default=False)
    seats = models.IntegerField(default=1)

    def get_orders(self):
        return json.loads(self.food_orders)

    def add_order(self, food, quantity):
        food = Food.objects.get(name=food)
        orders = self.get_orders()
        orders.append({food.name: quantity})
        self.food_orders = json.dumps(dict(orders))
        self.save()
        return food

    def can_cancel(self):
        return not self.cancelled and not self.used and self.show.time > timezone.now()

    def cancel(self):
        if not self.can_cancel():
            return False

        self.cancelled = True
        self.show.release_seats(self.seats)

        # Create refund transaction
        refund = Transaction.objects.create(
            user=self.user,
            amount=self.price,
            type="refund"
        )
        self.user.money += self.price
        self.user.save()

        # Refund food orders if any
        if self.food_orders:
            food_total = sum(order['price'] * order['quantity']
                             for order in self.get_orders())
            self.user.money += food_total
            self.user.save()

        self.save()
        return True

    def add_food_order(self, food_item, quantity):
        if self.show.time <= timezone.now():
            return False

        if self.food_orders is None:
            self.food_orders = []

        order = {
            'food_id': food_item.id,
            'name': food_item.name,
            'quantity': quantity,
            'price': food_item.price
        }

        orders = self.get_orders()
        orders.append(order)
        self.food_orders = json.dumps(orders)
        self.save()

        # Deduct money from user
        total = food_item.price * quantity
        self.user.money -= total
        self.user.save()

        return True
