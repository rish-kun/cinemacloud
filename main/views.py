import datetime
from django.shortcuts import render, redirect
from .models import User, Ticket, Show, Movie, Food, Transaction, TheatreAdmin, Theatre
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
