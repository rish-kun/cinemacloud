from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.models import User as DjangoUser
import datetime
from django.shortcuts import render, redirect
from .models import User, Ticket, Show, Movie, Food, Transaction, TheatreAdmin, Theatre, Screen
from django.views import View
import bcrypt
from .setup import setup
from django.http import HttpResponse, JsonResponse, Http404
from .utils import gen_otp
from .mail import send_email, email_body

# Account related views


class IndexView(View):
    def get(self, request):
        try:
            request.COOKIES['user-identity']
        except KeyError:
            return redirect("main:login")
        try:
            user = User.objects.get(uuid=request.COOKIES['user-identity'])
        except User.DoesNotExist:
            resp = redirect("main:login")
            resp.delete_cookie('user-identity')
            return resp
        show_list = [x for x in Show.objects.all() if x.is_bookable()]

        return render(request, "main/index.html", context={"user": user, "shows": show_list[::-1]})


class LoginView(View):
    def get(self, request):
        if not User.get_user(request, "login"):
            return redirect("main:index")
        return render(request, "main/login.html")

    def post(self, request):
        user = User.authenticate(User, request)
        if user:
            resp = redirect("main:index")
            resp.set_cookie('user-identity', user.uuid)
            return resp
        else:
            return render(request, "main/login.html", context={"error": "Invalid Credentials"})

        pass


class SignupView(View):
    def get(self, request):
        if not User.get_user(request, "signup"):
            return redirect("main:index")
        return render(request, "main/signup.html")

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        user = User.objects.create(email=email, password=bcrypt.hashpw(
            bytes(password, 'utf-8'), bcrypt.gensalt()), name=name.capitalize())
        user.create_wallet()
        user.save()
        resp = redirect("main:index")
        resp.set_cookie('user-identity', user.uuid)
        #

        return resp


class LogoutView(View):
    def get(self, request):
        return render(request, "404.html")

    def post(self, request):
        resp = redirect("main:login")
        resp.delete_cookie('user-identity')
        return resp


class AccountView(View):
    def get(self, request):
        try:
            request.COOKIES['user-identity']
        except KeyError:
            return redirect("main:login")
        try:
            user = User.objects.get(uuid=request.COOKIES['user-identity'])
        except User.DoesNotExist:
            resp = redirect("main:login")
            resp.delete_cookie('user-identity')
            return resp
        return render(request, "main/account.html", context={"user": user})


class PasswordChangeView(View):
    def get(self, request):
        return render(request, "main/password_change.html")

    def post(self, request):
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
        old_password = request.POST['current_password']
        new_password = request.POST['new_password']
        if bcrypt.checkpw(bytes(old_password, 'utf-8'), user.password):
            user.password = bcrypt.hashpw(
                bytes(new_password, 'utf-8'), bcrypt.gensalt())
            user.save()
            send_email("Your CinemaCloud password has been changed",
                       f"Your CinemaCloud password has been changed on {datetime.datetime.now()} ", [user.email])
            return redirect("/account?password_changed=true")
        return render(request, "main/password_change.html", context={"error": "Invalid Current Password", "user": user})


class AccountEditView(View):
    def get(self, request):
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
        return render(request, "main/account_edit.html", context={"user": user})

    def post(self, request):
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
        user.name = request.POST['name']
        user.email = request.POST['email']
        user.save()
        return redirect("/account?edit=true")


def setup_view(request):
    setup()
    return HttpResponse("Setup Done")


def setup_movies_view(request):
    setup(movies=True)
    return HttpResponse("Setup Done")


# ? Views related to booking/ticketing

class ShowView(View):
    def get(self, request, show_id: str):
        show = Show.objects.get(id=show_id)
        return render(request, "main/book.html", context={"show": show})


class BookView(View):
    def get(self, request):
        return HttpResponse("Nothing here")

    def post(self, request):
        n_t = int(request.POST['tickets'])
        show_id = request.POST['show_id']
        show = Show.objects.get(id=show_id)
        user = User.objects.get(uuid=request.COOKIES['user-identity'])

        if not show.is_bookable():
            return render(request, "main/book.html", {"error": "Show is not available for booking", "show": show})

        if not show.book_seats(n_t):
            return render(request, "main/book.html", {"error": "Not enough seats available", "show": show})

        total_price = n_t * show.price
        if user.wallet.money < total_price:
            return render(request, "main/book.html", {"error": "Insufficient funds", "show": show})
        th = TheatreAdmin.objects.first()
        transaction = Transaction(
            amount=total_price, type="ticket", user=user, to=th, otp=gen_otp())
        # send otp
        print(transaction.otp)
        send_email("OTP for CinemaCloud", email_body.format(
            otp=int(transaction.otp)), [user.email])
        transaction.save()
        # return otp check page
        return render(request, "main/transaction_verify.html", context={"show": show, "user": user, "tickets": n_t, "transaction": transaction, "redirect": "booking"})


class CancelTicketView(View):
    def get(self, request, ticket_id):
        return render(request, "main/confirm.html", context={"ticket": Ticket.objects.get(id=ticket_id), "user": User.objects.get(uuid=request.COOKIES['user-identity'])})

    def post(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        if str(ticket.user.uuid) != request.COOKIES['user-identity']:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        if ticket.cancel():
            return render(request, "main/ticket.html", context={"ticket": ticket, "user": ticket.user, "food_orders": ticket.get_orders(), "error": "Ticket cancelled successfully"})
        return render(request, "main/ticket.html", context={"ticket": ticket, "user": ticket.user, "food_orders": ticket.get_orders(), "error": "Ticket cannot be cancelled"})


class ConfirmTransactionView(View):
    def get(self, request, transaction_id):
        raise Http404

    def post(self, request, transaction_id):
        """get transaction from id
         confirm otp"""
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
        transaction = Transaction.objects.get(id=str(transaction_id))
        total_price = transaction.amount
        otp = int(str(request.POST['otp-1']) + str(request.POST['otp-2']) + str(request.POST['otp-3']) +
                  str(request.POST['otp-4']) +
                  str(request.POST['otp-5']) + str(request.POST['otp-6']))
        redir = request.POST['redirect']
        if redir == "booking":
            if otp == transaction.otp:
                tickets = request.POST['tickets']
                show = Show.objects.get(id=request.POST['show_id'])
                user.wallet.money -= total_price

                ticket = Ticket.objects.create(
                    user=user,
                    show=show,
                    price=total_price,
                    seats=tickets
                )
                transaction.executed = True
                user.bookings += 1
                # user.add_ticket(ticket)
                transaction.save()
                ticket.save()
                user.save()
                user.wallet.save()
                return render(request, "main/booked.html", context={"ticket": ticket})

        elif redir == "withdraw":
            if otp == transaction.otp:
                user.wallet.money -= total_price
                user.wallet.save()
                transaction.executed = True
                transaction.save()
                return redirect("/wallet?transaction=withdraw")
            return redirect("/wallet?wrong_otp=true")

        elif redir == "add":
            if otp == transaction.otp:
                user.wallet.money += total_price
                user.wallet.save()
                transaction.executed = True
                transaction.save()
                return redirect("/wallet?transaction=add")
            return redirect("/wallet?wrong_otp=true")

        elif redir == "food":
            if otp == transaction.otp:
                ticket_id = request.POST['ticket_id']
                ticket = Ticket.objects.get(id=ticket_id)
                ticket.food_order_confirmed = True
                ticket.food_order_price = transaction.amount
                ticket.save()
                user.wallet.money -= total_price
                user.wallet.save()
                transaction.executed = True
                transaction.save()
                return redirect(f"/ticket/{ticket_id}?meal_confirm=true")

        return JsonResponse({"error": "Invalid OTP"}, status=400)


def search_shows(request):
    query = request.GET.get('query').strip()
    print(query.lower())
    shows = []
    if query:
        for show in Show.objects.all():
            if query.lower() in show.movie.title.lower():
                shows.append(show)

    return render(request, 'main/shows_grid.html', {'shows': shows})


def not_found_404(request):
    return render(request, "404.html")


class TicketView(View):
    def get(self, request):
        try:
            request.COOKIES['user-identity']
        except KeyError:
            return redirect("main:login")
        try:
            user = User.objects.get(uuid=request.COOKIES['user-identity'])
        except User.DoesNotExist:
            resp = redirect("main:login")
            resp.delete_cookie('user-identity')
            return resp
        tickets = Ticket.objects.filter(user=user)
        return render(request, "main/tickets.html", context={"user": user, "tickets": tickets[::-1]})


def movies(request):
    movies = Movie.objects.all()
    return render(request, "main/movies.html", context={"movies": movies})


def shows(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    shows = Show.objects.filter(movie=movie)
    return render(request, "main/index.html", context={"shows": shows[::-1], "movie_name": movie.title})


class FoodOrderView(View):

    def get(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        print(Food.objects.all())
        return render(request, "main/food.html", context={"foods": Food.objects.all(), "user": ticket.user, "ticket": ticket})

    def post(self, request, ticket_id):
        print(request.COOKIES['user-identity'])
        print(ticket.user.uuid)
        if str(ticket.user.uuid) != request.COOKIES['user-identity']:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        order_list = {}
        total_price = 0
        for food in Food.objects.all():
            print(food.name)
            food_qty = int(request.POST[f'qty-{food.food_id}'])
            if food_qty != 0:
                ticket.add_order(food.id, food_qty)
                order_list[food.food_id] = food_qty
            total_price += food.price * food_qty
        if total_price > ticket.user.wallet.money:
            return render(request, "main/food.html", context={"error": "Insufficient funds", "foods": Food.objects.all(), "user": ticket.user, "ticket": ticket})
        transaction = Transaction(
            amount=total_price, type="food", user=ticket.user, otp=gen_otp())
        send_email("OTP for CinemaCloud", email_body.format(
            otp=int(transaction.otp)), [ticket.user.email])
        print(transaction.otp)
        print(transaction.id)
        transaction.save()

        return render(request, "main/transaction_verify.html", context={"user": ticket.user, "transaction": transaction, "redirect": "food", "ticket": ticket})


def ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    print("here")
    return render(request, "main/ticket.html", context={"ticket": ticket, "user": ticket.user, "food_orders": ticket.get_orders()})


def theatres(request):
    return render(request, "main/theatres.html", context={"theatres": Theatre.objects.all()})


def theatre(request, theatre_id):
    theatre = Theatre.objects.get(id=theatre_id)
    return render(request, "main/theatre.html", context={"theatre": theatre, "shows": Show.objects.filter(theatre=theatre)})

# Views related to wallet


def transactions(request):
    user = User.objects.get(uuid=request.COOKIES['user-identity'])
    transactions = Transaction.objects.filter(user=user)
    return render(request, "main/transactions.html", context={"transactions": transactions[::-1], "user": user})


def transaction(request, transaction_id):
    user = User.objects.get(uuid=request.COOKIES['user-identity'])
    transaction = Transaction.objects.get(id=transaction_id)
    return render(request, "main/transaction.html", context={"transaction": transaction, "user": user})


def withdraw(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = User.objects.get(uuid=request.COOKIES['user-identity'])
    amount = int(request.POST['amount'])
    if user.wallet.money < amount:
        return render(request, "main/wallet.html", context={"error": "Insufficient funds", "user": user})
    transaction = Transaction.objects.create(
        user=user,
        amount=amount,
        type="withdraw", otp=gen_otp())
    print(transaction.otp)
    send_email("OTP for CinemaCloud", email_body.format(
        otp=int(transaction.otp)), [user.email])
    transaction.save()
    return render(request, "main/transaction_verify.html", context={"user": user, "transaction": transaction, "redirect": "withdraw"})


def add(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = User.objects.get(uuid=request.COOKIES['user-identity'])
    amount = int(request.POST['amount'])
    transaction = Transaction.objects.create(
        user=user,
        amount=amount,
        type="add", otp=gen_otp())
    print(transaction.otp)
    send_email("OTP for CinemaCloud", email_body.format(
        otp=int(transaction.otp)), [user.email])
    transaction.save()
    return render(request, "main/transaction_verify.html", context={"user": user, "transaction": transaction, "redirect": "add"})


def wallet(request):
    try:
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
    except User.DoesNotExist:
        resp = redirect("main:login")
        resp.delete_cookie('user-identity')
        return resp

    return render(request, "main/wallet.html", context={"user": user, "transactions": user.get_transactions()[::-1]})


# Theatre Admin Views

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
        print("here1")
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = DjangoUser.objects.get(username=username)
        except DjangoUser.DoesNotExist:
            # return error
            return redirect("main:index")
        if user.check_password(password) and on_admin_group(user):
            if user.last_login == None:
                available_theatres = Theatre.objects.filter(admin_uuid=None)
                login(request, user,
                      backend="django.contrib.auth.backends.ModelBackend")
                return render(request, "th_admin/register_th_admin.html", context={"user": user, "theatres": available_theatres})
            print("here")
            login(request, user,
                  backend="django.contrib.auth.backends.ModelBackend")
            print("here")
            return redirect("main:th_admin_home")
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
        return render(request, "th_admin/food.html", context={"foods": Food.objects.all()})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class EditFoodView(View):
    def get(self, request, food_id):
        food = Food.objects.get(id=food_id)
        return render(request, "th_admin/edit_food.html", context={"food": food})

    def post(self, request, food_id):
        # make method such that it updates the food items
        name = request.POST['name']
        price = int(request.POST['price'])
        descrpiton = request.POST['description']
        category = request.POST['category']
        image = request.POST['image']
        food = Food.objects.get(id=food_id)
        food.name = name
        food.price = price
        food.category = category
        food.description = descrpiton
        food.image = image
        food.save()
        return redirect("main:th_admin_food")


class AddFoodView(View):
    def get(self, request):
        return render(request, "th_admin/add_food.html")

    def post(self, request):
        name = request.POST['name']
        price = int(request.POST['price'])
        description = request.POST['description']
        category = request.POST['category']
        image = request.POST['image']
        food = Food.objects.create(
            name=name, price=price, description=description, category=category, image=image)
        food.save()
        return redirect("main:th_admin_food")


def delete_food_item(request, food_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    food = Food.objects.get(id=food_id)
    food.delete()
    return redirect("main:th_admin_food")


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class AdminShowView(View):
    def get(self, request):
        user = request.user
        th_admin = TheatreAdmin.objects.get(user=user)
        return render(request, "th_admin/shows.html", context={"shows": th_admin.theatre.get_shows()})

    # shows the tickets booked for the show
    def post(self, request):
        show_id = request.POST['show_id']
        show = Show.objects.get(id=show_id)
        return render(request, "th_admin/show_tickets.html", context={"show": show, "tickets": show.get_tickets()})


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class AddShowView(View):
    def get(self, request):
        user = request.user
        th_admin = TheatreAdmin.objects.get(user=user)
        theatre = th_admin.theatre
        return render(request, "th_admin/add_show.html", context={"movies": Movie.objects.all(), "screens": theatre.get_screens()})

    def post(self, request):
        # add show with given details
        movie_id = request.POST['movie']
        date = request.POST['show_date']
        time = request.POST['show_time']
        screen_id = request.POST['screen_id']
        available_seats = request.POST['seats']
        price = request.POST['price']
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        show = Show.objects.create(movie=Movie.objects.get(id=movie_id), theatre=TheatreAdmin.objects.get(
            user=request.user).theatre, time=dt, screen=Screen.objects.get(id=screen_id), available_seats=available_seats, price=price)
        if dt < datetime.datetime.now():
            show.is_active = False

        show.save()
        return redirect("main:th_admin_show")


@method_decorator(user_passes_test(on_admin_group, login_url="main:th_admin"), name="dispatch")
class EditShowView(View):
    def get(self, request, show_id):
        show = Show.objects.get(id=show_id)
        theatre = TheatreAdmin.objects.get(user=request.user).theatre
        return render(request, "th_admin/edit_show.html", context={"show": show, "theatre": theatre, "screens": theatre.get_screens()})

    def post(self, request, show_id):
        date = request.POST['date']
        time = request.POST['time']
        price = request.POST['price']
        screen_id = request.POST['screen_id']
        show = Show.objects.get(id=show_id)
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        show.time = dt
        show.price = price
        show.screen = Screen.objects.get(id=screen_id)
        show.save()
        return redirect("main:th_admin_show")


def delete_show_view(request, show_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    show = Show.objects.get(id=show_id)
    show.delete()
    return redirect("main:th_admin_show")

# Theatre Admin screen views


def screen_view(request):
    user = request.user
    theatre = TheatreAdmin.objects.get(user=user).theatre
    return render(request, "th_admin/screens.html", context={"screens": theatre.get_screens()})


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
        return redirect("main:th_admin_screen")


class EditScreenView(View):
    def get(self, request, screen_id):
        screen = Screen.objects.get(id=screen_id)
        return render(request, "th_admin/edit_screen.html", context={"screen": screen})

    def post(self, request, screen_id):
        screen_number = request.POST['screen_number']
        seats = request.POST['seats']
        screen_type = request.POST['screen_type']
        screen = Screen.objects.get(id=screen_id)
        screen.screen_number = screen_number
        screen.seats = seats
        screen.type = screen_type
        screen.save()
        return redirect("main:th_admin_screen")


def delete_screen_view(request, screen_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    # delete screen with given id
    theatre = TheatreAdmin.objects.get(user=request.user).theatre
    if str(theatre.default_screen_id) == str(screen_id):
        return redirect("/th_admin/screens?error=true")
    screen = Screen.objects.get(id=screen_id)
    screen.delete()
    return redirect("main:th_admin_screen")


def admin_booking_view(request):
    # get all bookings of the theatre
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


def admin_ticket_details(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, "th_admin/ticket_details.html", context={"ticket": ticket, "food_orders": ticket.get_orders()})


def admin_ticket_used(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    ticket_id = request.POST['ticket_id']
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.status = "used"
    ticket.save()
    return redirect("main:th_admin_bookings")


def admin_ticket_cancel(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    ticket_id = request.POST['ticket_id']
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.cancel()
    ticket.save()
    return redirect("main:th_admin_bookings")


def register_th_admin(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user: DjangoUser = request.user
    theatre_id = request.POST['theatre']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    phone = request.POST['phone']
    theatre = Theatre.objects.get(id=theatre_id)
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
    return redirect("main:th_admin_home")
