import json
from django.db import models
import uuid
import bcrypt
from django.shortcuts import redirect
from django.utils import timezone
import random
from django.conf import settings
# from django.contrib.postgres.fields import ArrayField


class Wallet(models.Model):
    money = models.IntegerField(default=100)
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
    password = models.BinaryField(max_length=255)
    name = models.CharField(max_length=255)
    tickets = models.JSONField(default=list, null=True)
    # tickets = models.ArrayField(default=None, null=True)

    creation_date = models.DateTimeField(
        auto_now_add=True, null=True)
    # money = models.IntegerField(default=1000)
    # transaction_history = models.JSONField(default=None, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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

    def get_current_ticket(self):
        pass

    def add_ticket(self, ticket):
        if self.tickets is not None:
            t_s = json.loads(self.tickets)
        else:
            t_s = []
        if t_s is None:
            t_s = []
        t_s.append(ticket.id)
        self.tickets.append(ticket)
        self.save()

    def authenticate(self, request):
        email = request.POST['email']
        password = request.POST['password']
        if bcrypt.checkpw(bytes(password, 'utf-8'), User.objects.get(email=email).password):
            user = User.objects.get(email=email)
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
    shows = models.JSONField(null=True, default=None, blank=True)
    admin_uuid = models.UUIDField(default=None, null=True, blank=True)
    default_screen_id = models.UUIDField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

    def get_shows(self):
        return Show.objects.filter(theatre=self)

    def get_screens(self):
        return Screen.objects.filter(theatre=self)

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
        return sc

    def get_default_screen(self):
        return Screen.objects.get(id=self.default_screen_id)


class TheatreAdmin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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


class Transaction(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    type = models.CharField(max_length=255, choices=[(
        "add", "add"), ("withdraw", "withdraw"), ("refund", "refund"), ("ticket", "ticket"), ("food", "food")], null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    otp = models.IntegerField(default=random.randint(
        100000, 999999), unique=False, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False,
                          unique=True, primary_key=True)
    executed = models.BooleanField(default=False)
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
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=[(
        'snacks', 'snacks'), ('beverages', 'beverages'), ('combos', 'combos')], default='snacks')
    food_id = models.BigIntegerField(null=True, unique=True, default=None)

    def __str__(self):
        return self.name


class Screen(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    screen_number = models.IntegerField()
    seats = models.JSONField(default=None, null=True)
    type = models.CharField(max_length=255, choices=[
                            ('2D', '2D'), ('3D', '3D'), ('IMAX', 'IMAX')], default='2D')
    # seats = models.ArrayField(default=None, null=True)

    def __str__(self):
        return f"{self.theatre.name} - {self.screen_number}"


class Show(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
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
    id = models.UUIDField(default=uuid.uuid4, editable=False,
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

    def add_order(self, food_id: uuid.UUID, quantity: int):
        food = Food.objects.get(id=food_id)
        if self.food_orders is not None and self.food_orders != "" and len(self.food_orders) != 0:
            orders = json.loads(self.food_orders)
        else:
            orders = {}
        orders.update({food.food_id: quantity})
        self.food_orders = json.dumps(orders)
        self.save()
        return True

    def can_cancel(self):
        return not self.cancelled and not self.used and self.show.time > timezone.now()

    def cancel(self):
        if not self.can_cancel():
            return False

        self.cancelled = True
        self.status = "cancelled"
        self.show.release_seats(self.seats)

        refund = Transaction.objects.create(
            user=self.user,
            amount=self.price+self.food_order_price,
            type="refund", executed=True
        )
        refund.save()
        self.user.wallet.money += (self.price+self.food_order_price)
        self.user.save()
        self.user.wallet.save()
        self.save()
        return True
