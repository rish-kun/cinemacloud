from django.shortcuts import render, redirect
import random
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.models import User as DjangoUser
from main.models import Ticket, Show, Movie, Food, TheatreAdmin, Theatre, Screen, Transaction
from django.http import JsonResponse
from django.views import View
import datetime


def is_on_group_check(*groups):
    def on_group_check(user):
        if user.groups is None:
            return False
        return user.groups.filter(name__in=groups).exists()
    return on_group_check


on_admin_group = is_on_group_check("TheatreAdmin")


class AdminLoginView(View):
    def get(self, request):
        return render(request, "th_admin/login.html")

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = DjangoUser.objects.get(username=username)
        except DjangoUser.DoesNotExist:
            return render(request, "error.html", context={"error": "Invalid Credentials"})
        if user.check_password(password) and on_admin_group(user):
            if user.last_login == None:
                available_theatres = Theatre.objects.filter(admin_uuid=None)
                login(request, user,
                      backend="django.contrib.auth.backends.ModelBackend")
                return render(request, "th_admin/register_th_admin.html", context={"user": user, "theatres": available_theatres})
            login(request, user,
                  backend="django.contrib.auth.backends.ModelBackend")
            return redirect("th_admin:home")
        return render(request, "th_admin/login.html", context={"error": "Invalid Credentials"})


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_logout(request):
    logout(request)
    return redirect("main:th_admin")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_home(request):
    th_admin = TheatreAdmin.objects.get(user=request.user)
    today_shows = th_admin.theatre.get_today_shows()
    screens = th_admin.theatre.get_screens().count()
    return render(request, "th_admin/home.html", context={"theatre": TheatreAdmin.objects.get(user=request.user).theatre, "user": TheatreAdmin.objects.get(user=request.user), "today_shows": today_shows, "screens": screens})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class AdminFoodView(View):
    def get(self, request):
        user = request.user
        th_admin = TheatreAdmin.objects.get(user=user)
        return render(request, "th_admin/food.html", context={"foods": th_admin.theatre.get_food()})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class EditFoodView(View):
    def get(self, request, food_id):
        food = Food.objects.get(uuid=food_id)
        return render(request, "th_admin/edit_food.html", context={"food": food})

    def post(self, request, food_id):
        name = request.POST['name']
        price = int(request.POST['price'])
        descrpiton = request.POST['description']
        category = request.POST['category']
        image = request.POST['image']
        food = Food.objects.get(uuid=food_id)
        food.name = name
        food.price = price
        food.category = category
        food.description = descrpiton
        food.image = image
        food.save()
        return redirect("th_admin:food")


class AddFoodView(View):
    def get(self, request):
        return render(request, "th_admin/add_food.html")

    def post(self, request):
        name = request.POST['name']
        price = int(request.POST['price'])
        description = request.POST['description']
        category = request.POST['category']
        image = request.POST['image']
        food_id = random.randint(100000, 999999)
        food = Food.objects.create(
            name=name, price=price, description=description, category=category, image=image, food_id=food_id)
        food.theatre = TheatreAdmin.objects.get(user=request.user).theatre
        food.save()
        return redirect("th_admin:food")


def delete_food_item(request, food_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    food = Food.objects.get(uuid=food_id)
    food.delete()
    return redirect("th_admin:food")


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class AdminShowView(View):
    def get(self, request):
        user = request.user
        th_admin = TheatreAdmin.objects.get(user=user)
        return render(request, "th_admin/shows.html", context={"shows": th_admin.theatre.get_shows()})

    def post(self, request):
        show_id = request.POST['show_id']
        show = Show.objects.get(uuid=show_id)
        return render(request, "th_admin/show_tickets.html", context={"show": show, "tickets": show.get_tickets()})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class AddShowView(View):
    def get(self, request):
        user = request.user
        th_admin = TheatreAdmin.objects.get(user=user)
        theatre = th_admin.theatre
        return render(request, "th_admin/add_show.html", context={"movies": Movie.objects.all(), "screens": theatre.get_screens()})

    def post(self, request):
        movie_id = request.POST['movie']
        date = request.POST['show_date']
        time = request.POST['show_time']
        screen_id = request.POST['screen_id']
        available_seats = request.POST['seats']
        price = request.POST['price']
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        show = Show.objects.create(movie=Movie.objects.get(uuid=movie_id), theatre=TheatreAdmin.objects.get(
            user=request.user).theatre, time=dt, screen=Screen.objects.get(uuid=screen_id), available_seats=available_seats, price=price)
        if dt < datetime.datetime.now():
            show.is_active = False

        show.save()
        return redirect("th_admin:show")


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class EditShowView(View):
    def get(self, request, show_id):
        show = Show.objects.get(uuid=show_id)
        theatre = TheatreAdmin.objects.get(user=request.user).theatre
        return render(request, "th_admin/edit_show.html", context={"show": show, "theatre": theatre, "screens": theatre.get_screens()})

    def post(self, request, show_id):
        date = request.POST['date']
        time = request.POST['time']
        price = request.POST['price']
        screen_id = request.POST['screen_id']
        show = Show.objects.get(uuid=show_id)
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        show.time = dt
        show.price = price
        show.screen = Screen.objects.get(uuid=screen_id)
        show.save()
        return redirect("th_admin:show")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def delete_show_view(request, show_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    show = Show.objects.get(uuid=show_id)
    show.delete()
    return redirect("th_admin:show")

# Theatre Admin screen views


@user_passes_test(on_admin_group, login_url="main:th_admin")
def screen_view(request):
    user = request.user
    theatre = TheatreAdmin.objects.get(user=user).theatre
    return render(request, "th_admin/screens.html", context={"screens": theatre.get_screens()})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class AddScreenView(View):
    def get(self, request):
        user = request.user
        return render(request, "th_admin/add_screen.html", context={"theatre": TheatreAdmin.objects.get(user=user).theatre})

    def post(self, request):
        screen_number = request.POST['screen_number']
        seats = request.POST['seats']
        screen_type = request.POST['screen_type']
        theatre = TheatreAdmin.objects.get(user=request.user).theatre
        screen = Screen.objects.create(
            theatre=theatre, screen_number=screen_number, seats=seats, type=screen_type)
        screen.save()
        return redirect("th_admin:screen")


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class EditScreenView(View):
    def get(self, request, screen_id):
        screen = Screen.objects.get(uuid=screen_id)
        return render(request, "th_admin/edit_screen.html", context={"screen": screen})

    def post(self, request, screen_id):
        screen_number = request.POST['screen_number']
        seats = request.POST['seats']
        screen_type = request.POST['screen_type']
        screen = Screen.objects.get(uuid=screen_id)
        screen.screen_number = screen_number
        screen.seats = seats
        screen.type = screen_type
        screen.save()
        return redirect("th_admin:screen")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def delete_screen_view(request, screen_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    # delete screen with given id
    theatre = TheatreAdmin.objects.get(user=request.user).theatre
    if str(theatre.default_screen_id) == str(screen_id):
        return redirect("/th_admin/screens?error=true")
    screen = Screen.objects.get(uuid=screen_id)
    screen.delete()
    return redirect("th_admin:screen")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_booking_view(request):
    theatre = TheatreAdmin.objects.get(user=request.user).theatre
    bookings = theatre.get_bookings()
    today_bookings = 0
    for booking in bookings:
        if booking.show.time.date == datetime.datetime.now().date():
            today_bookings += 1
    total_booked = bookings.filter(status="booked").count()
    total_completed = bookings.filter(status="used").count()
    total_cancelled = bookings.filter(status="cancelled").count()
    return render(request, "th_admin/bookings.html", context={"bookings": bookings, "total_booked": total_booked, "total_completed": total_completed, "total_cancelled": total_cancelled, "today_bookings": today_bookings})


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_ticket_details(request, ticket_id):
    ticket = Ticket.objects.get(uuid=ticket_id)
    return render(request, "th_admin/ticket_details.html", context={"ticket": ticket, "food_orders": ticket.get_orders()})


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_ticket_used(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    ticket_id = request.POST['ticket_id']
    ticket = Ticket.objects.get(uuid=ticket_id)
    ticket.status = "used"
    ticket.save()
    return redirect("th_admin:bookings")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_ticket_cancel(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    ticket_id = request.POST['ticket_id']
    ticket = Ticket.objects.get(uuid=ticket_id)
    ticket.cancel()
    ticket.save()
    return redirect("th_admin:bookings")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def register_th_admin(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user: DjangoUser = request.user
    theatre_id = request.POST['theatre']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    theatre = Theatre.objects.get(uuid=theatre_id)
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    th_admin = TheatreAdmin.objects.create(
        user=user, phone=phone)
    th_admin.theatre = theatre
    user.save()

    th_admin.create_wallet()
    th_admin.save()
    theatre.admin_uuid = th_admin.uuid
    sc = theatre.create_def_screen()
    sc.save()
    theatre.save()
    return redirect("th_admin:home")


@user_passes_test(on_admin_group, login_url="main:th_admin")
def admin_wallet_view(request):
    th_admin = TheatreAdmin.objects.get(user=request.user)

    return render(request, "th_admin/wallet.html", context={"user": th_admin, "wallet": th_admin.wallet, "revenue": th_admin.theatre.get_revenue(), "transactions": th_admin.get_transactions(), "food_revenue": th_admin.get_revenue_by_food(), "ticket_revenue": th_admin.get_revenue_by_ticket()})


@user_passes_test(on_admin_group, login_url="main:th_admin")
def transactions(request):
    user = request.user
    th_admin = TheatreAdmin.objects.get(user=user)
    th_admin.get_transactions()
    return render(request, "th_admin/transactions.html", context={"transactions": th_admin.get_transactions()})


@user_passes_test(on_admin_group, login_url="main:th_admin")
def transaction(request, transaction_id):
    transaction = Transaction.objects.get(uuid=transaction_id)
    return render(request, "th_admin/transaction.html", context={"transaction": transaction})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class TheatreView(View):
    def get(self, request):
        return render(request, "th_admin/theatre.html", context={"theatre": TheatreAdmin.objects.get(user=request.user).theatre})

    def post(self, request):
        name = request.POST['name']
        location = request.POST['location']
        theatre = TheatreAdmin.objects.get(user=request.user).theatre
        theatre.name = name
        theatre.location = location
        theatre.save()
        return redirect("th_admin:home")
