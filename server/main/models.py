import json
from django.db import models
import uuid as uuid_module
import bcrypt
from django.shortcuts import redirect
from django.utils import timezone
import random
from .mail import send_email, t_complete, verification_email
from django.conf import settings


class Wallet(models.Model):
    money = models.PositiveIntegerField(default=1000)
    user_id = models.UUIDField(default=None, null=True)
    transaction_history = models.JSONField(null=True)
    th_admin_wallet = models.BooleanField(default=False)

    def __str__(self):
        if self.th_admin_wallet:
            th_admin = TheatreAdmin.objects.get(uuid=self.user_id)
            return f"{th_admin.user.username} - {self.money}"
        user = User.objects.get(uuid=self.user_id)
        return f"{user.name} - {self.money}"


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.BinaryField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    tickets = models.JSONField(default=list, null=True)
    creation_date = models.DateTimeField(
        auto_now_add=True, null=True)
    google_account = models.BooleanField(default=False, editable=False)
    uuid = models.UUIDField(default=uuid_module.uuid4,
                            editable=False, unique=True)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, default=None, null=True)
    email_verified = models.BooleanField(default=False)
    bookings = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.email}"

    def create_wallet(self):

        self.wallet = Wallet.objects.create(user_id=self.uuid)
        self.wallet.save()
        self.save()

    def get_tickets(self):
        return Ticket.objects.filter(user=self)

    def add_ticket(self, ticket):
        if self.tickets is not None:
            t_s = json.loads(self.tickets)
        else:
            t_s = []
        if t_s is None:
            t_s = []
        t_s.append(ticket.uuid)
        self.tickets.append(ticket)
        self.save()

    def authenticate(self, request=None, email=None, password=None):
        if request:
            email = request.POST['email']
            password = request.POST['password']
        user = User.objects.get(email=email)

        if type(user.password) == memoryview:
            if bcrypt.checkpw(bytes(password, 'utf-8'), user.password.tobytes()):
                return user
        elif bcrypt.checkpw(bytes(password, 'utf-8'), user.password):
            return user
        return None

    def get_transactions(self):
        transactions = Transaction.objects.filter(user=self)
        return transactions

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

    def send_verification_email(self, request):
        query = VerificationQuery.objects.create(user=self)
        link = f"{
            request.scheme}://{request.META['HTTP_HOST']}/verify/{query.uuid}/{self.uuid}"
        send_email("Email Verification for CinemaCloud", verification_email.format(
            verification_link=link), [self.email])
        return True

    @staticmethod
    def check_verification(query_id, uuid):
        query = VerificationQuery.objects.get(uuid=query_id)
        if query.user == User.objects.get(uuid=uuid):
            query.user.email_verified = True
            query.user.save()
            return True
        return False


class Log(models.Model):
    info = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=255, choices=[(
        'INFO', 'INFO'), ('ERROR', 'ERROR'), ('WARNING', 'WARNING')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pass


class Theatre(models.Model):
    uuid = models.UUIDField(
        default=uuid_module.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    shows = models.JSONField(null=True, default=None, blank=True)
    admin_uuid = models.UUIDField(default=None, null=True, blank=True)
    default_screen_id = models.UUIDField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

    def get_shows(self):
        return Show.objects.filter(theatre=self)

    def get_screens(self):
        return Screen.objects.filter(theatre=self)

    def get_food(self):
        return Food.objects.filter(theatre=self)

    def get_admin(self):
        return TheatreAdmin.objects.get(uuid=self.admin_uuid)

    def get_movies(self):
        shows = self.get_shows()
        movies = []
        for show in shows:
            movies.append(show.movie)
        return movies

    def get_bookings(self):
        return Ticket.objects.filter(show__theatre=self)

    def get_today_shows(self):
        shows = Show.objects.filter(theatre=self)
        today = timezone.now().date()
        today_shows = []
        for show in shows:
            if show.time.date() == today:
                today_shows.append(show)
        return today_shows

    def create_def_screen(self):
        if self.default_screen_id is not None:
            return
        sc = Screen.objects.create(theatre=self, screen_number=1, seats=100)
        self.default_screen_id = sc.uuid
        self.save()
        return sc

    def get_default_screen(self):
        return Screen.objects.get(uuid=self.default_screen_id)

    def get_revenue(self):
        revenue = 0
        for ticket in self.get_bookings():
            if ticket.status == "used" or ticket.status == "booked":
                revenue += (ticket.price+ticket.food_order_price)

        return revenue


class TheatreAdmin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, unique=True)
    uuid = models.UUIDField(default=uuid_module.uuid4,
                            editable=False, unique=True)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, default=None, null=True, blank=True)
    theatre = models.ForeignKey(
        Theatre, on_delete=models.CASCADE, default=None, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.uuid}"

    class Meta:
        permissions = (("theateradmin", "User is a theater admin"),)

    def create_wallet(self):
        self.wallet = Wallet.objects.create(user_id=self.uuid)
        self.wallet.th_admin_wallet = True
        self.wallet.save()
        self.save()

    def get_transactions(self):
        transactions = Transaction.objects.filter(to=self)
        return transactions

    def get_revenue_by_food(self):
        revenue = 0
        for transaction in self.get_transactions():
            if transaction.type == "food":
                revenue += transaction.amount
        return revenue

    def get_revenue_by_ticket(self):
        revenue = 0
        for transaction in self.get_transactions():
            if transaction.type == "ticket":
                revenue += transaction.amount
        return revenue


class Transaction(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    type = models.CharField(max_length=255, choices=[(
        "add", "add"), ("withdraw", "withdraw"), ("refund", "refund"), ("ticket", "ticket"), ("food", "food")], null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    otp = models.IntegerField(default=random.randint(
        100000, 999999), unique=False, editable=False)
    uuid = models.UUIDField(default=uuid_module.uuid4, editable=False,
                            unique=True, primary_key=True)
    executed = models.BooleanField(default=False)
    status = models.CharField(max_length=255, choices=[(
        'INCOMPLETE', 'INCOMPLETE'), ('COMPLETE', 'COMPLETE'), ('REVERTED', 'REVERTED')], default='INCOMPLETE')
    to = models.ForeignKey(TheatreAdmin, on_delete=models.CASCADE, null=True)

    def send_transaction_complete_email(self):
        send_email("Transaction Complete", t_complete.format(
            amount=self.amount, type=self.type), [self.user.email,])
        return True

    def execute(self):
        if self.executed:
            return False
        if self.type == "add":
            self.user.wallet.money += self.amount
            self.user.save()
        elif self.type == "withdraw":
            self.user.wallet.money -= self.amount
            self.user.save()
        elif self.type == "refund":
            self.user.wallet.money += self.amount
            self.to.wallet.money -= self.amount
            self.to.wallet.save()
            self.to.save()
        elif self.type == "ticket" or self.type == "food":
            self.user.wallet.money -= self.amount
            self.to.wallet.money += self.amount
            self.to.wallet.save()
            self.to.save()

        self.executed = True
        self.status = "COMPLETE"
        self.user.wallet.save()
        self.user.save()
        self.save()
        self.send_transaction_complete_email()
        return True

    def refund(self):
        if self.type == "food" or self.type == "ticket":
            self.user.wallet.money += self.amount
            self.to.wallet.money -= self.amount
            self.status = "REVERTED"
            self.to.wallet.save()
            self.to.save()
            self.user.wallet.save()
            self.user.save()
            self.save()
            return True
        return True


class Movie(models.Model):
    uuid = models.UUIDField(default=uuid_module.uuid4,
                            editable=False, unique=True)
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
    uuid = models.UUIDField(
        default=uuid_module.uuid4,  editable=False, unique=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=[(
        'snacks', 'snacks'), ('beverages', 'beverages'), ('combos', 'combos')], default='snacks')
    food_id = models.BigIntegerField(null=True, unique=True, default=None)
    theatre = models.ForeignKey(
        Theatre, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.name


class Screen(models.Model):
    uuid = models.UUIDField(
        default=uuid_module.uuid4, editable=False, unique=True)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    screen_number = models.IntegerField()
    seats = models.JSONField(default=None, null=True)
    type = models.CharField(max_length=255, choices=[
                            ('2D', '2D'), ('3D', '3D'), ('IMAX', 'IMAX')], default='2D')

    def __str__(self):
        return f"{self.theatre.name} - {self.screen_number}"


class Show(models.Model):
    uuid = models.UUIDField(
        default=uuid_module.uuid4, editable=False, unique=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    time = models.DateTimeField()
    price = models.IntegerField()
    available_seats = models.IntegerField(default=100, null=False)
    screen = models.ForeignKey(Screen, default=1, on_delete=models.CASCADE)
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

    def get_tickets(self):
        return Ticket.objects.filter(show=self)


class Ticket(models.Model):
    uuid = models.UUIDField(default=uuid_module.uuid4, editable=False,
                            unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_date = models.DateTimeField(auto_now_add=True)
    price = models.BigIntegerField(default=100)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, null=True)
    food_orders = models.JSONField(
        default=None, null=True)  # ? format: {Food_item: quantity}
    cancelled = models.BooleanField(default=False)
    show = models.ForeignKey(
        Show, on_delete=models.CASCADE, null=True, default=None)
    used = models.BooleanField(default=False)
    seats = models.IntegerField(default=1)
    status = models.CharField(max_length=255, choices=[(
        'booked', 'booked'), ('cancelled', 'cancelled'), ('used', 'used')], default='booked')
    food_order_confirmed = models.BooleanField(default=False)
    food_order_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.name} - {self.show.movie.title} - {self.show.time}"

    def get_orders(self):
        if self.food_orders is not None and self.food_orders != "" and len(self.food_orders) != 0:
            orders = json.loads(self.food_orders)
        else:
            orders = {}
        o_l = {}
        for food_id in orders:
            food = Food.objects.get(food_id=food_id)
            o_l[food] = orders[food_id]
        return o_l

    def add_order(self, food_id: uuid_module.UUID, quantity: int):
        food = Food.objects.get(uuid=food_id)
        if self.food_orders is not None and self.food_orders != "" and len(self.food_orders) != 0:
            orders = json.loads(self.food_orders)
        else:
            orders = {}
        orders.update({food.food_id: quantity})
        self.food_orders = json.dumps(orders)
        self.save()
        return True

    def can_cancel(self):
        return (not self.cancelled and not self.used and self.show.time > timezone.now())

    def cancel(self):
        if not self.can_cancel():
            return False
        self.cancelled = True
        self.status = "cancelled"
        self.show.release_seats(self.seats)
        self.transaction.refund()
        self.save()
        return True


class VerificationQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    uuid = models.UUIDField(default=uuid_module.uuid4, unique=True)

    def url(self):
        return f"/verify/{self.uuid}/{self.user.uuid}"
