from django.shortcuts import render, redirect
from .models import User, Ticket, Show, Movie, Food, Transaction, TheatreAdmin
from django.views import View
import bcrypt
from .setup import setup
from django.http import HttpResponse
from django.http import JsonResponse

# TODO: Add otp for all transactions
# TODO: make transaction page into wallet page and change renders to redirect for add, withdraw transactions


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
        show_list = Show.objects.all()

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
            bytes(password, 'utf-8'), bcrypt.gensalt()), name=name)
        user.create_wallet()
        user.save()
        resp = redirect("main:index")
        resp.set_cookie('user-identity', user.uuid)
        # send_email
        return resp


class LogoutView(View):
    def get(self, request):
        return render(request, "404.html")

    def post(self, request):
        resp = redirect("main:login")
        resp.delete_cookie('user-identity')
        return resp


class MovieView(View):
    def get(self, request, movie_id):
        mov = Movie.objects.get(movie_id=movie_id)
        print(mov.json())
        # fetch movie from id and then show movie information and show option to book movie ticket
        return render(request, "main/movie.html", context={"movie": mov})

    def post(self, request, movie_id):
        mov = Movie.objects.get(movie_id=movie_id)
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
        ticket = Ticket.objects.create(
            user=user, )
        pass


def setup_view(request):
    setup()
    return HttpResponse("Setup Done")


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
        # add otp verification mechanism
        th = TheatreAdmin.objects.first()
        transaction = Transaction(
            amount=total_price, type="ticket", user=user, to=th)
        # send otp
        print(transaction.otp)
        print(transaction.id)
        transaction.save()
        # return otp check page
        return render(request, "main/transaction.html", context={"show": show, "user": user, "tickets": n_t, "transaction": transaction})


class ConfirmTransactionView(View):
    def post(self, request, transaction_id):
        # get transaction from id
        # confirm otp
        # create booking, and show confirmation
        # also get show id, ticketsfrom request.POST
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
        transaction = Transaction.objects.get(id=str(transaction_id))
        total_price = transaction.amount
        tickets = request.POST['tickets']
        otp = int(str(request.POST['otp-1']) + str(request.POST['otp-2']) + str(request.POST['otp-3']) +
                  str(request.POST['otp-4']) +
                  str(request.POST['otp-5']) + str(request.POST['otp-6']))
        show = Show.objects.get(id=request.POST['show_id'])
        if otp == transaction.otp:
            user.wallet.money -= total_price
            user.save()
            user.wallet.save()
            ticket = Ticket.objects.create(
                user=user,
                show=show,
                price=total_price,
                seats=tickets
            )
            return render(request, "main/booked.html", context={"ticket": ticket})
        # make error handling better
        return JsonResponse({"error": "Invalid OTP"}, status=400)


class CancelTicketView(View):
    def post(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.user.uuid != request.COOKIES['user-identity']:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        if ticket.cancel():
            return JsonResponse({"message": "Ticket cancelled successfully"})
        return JsonResponse({"error": "Cannot cancel ticket"}, status=400)


class FoodOrderView(View):
    def post(self, request, ticket_id):
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.user.uuid != request.COOKIES['user-identity']:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        food_id = request.POST['food_id']
        quantity = int(request.POST['quantity'])

        food_item = Food.objects.get(id=food_id)
        total_cost = food_item.price * quantity

        if ticket.user.wallet.money < total_cost:
            return JsonResponse({"error": "Insufficient funds"}, status=400)

        if ticket.add_food_order(food_item, quantity):
            return JsonResponse({"message": "Food order added successfully"})
        return JsonResponse({"error": "Cannot add food order"}, status=400)


def wallet(request):
    try:
        user = User.objects.get(uuid=request.COOKIES['user-identity'])
    except User.DoesNotExist:
        resp = redirect("main:login")
        resp.delete_cookie('user-identity')
        return resp

    return render(request, "main/wallet.html", context={"user": user})


def withdraw(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = User.objects.get(uuid=request.COOKIES['user-identity'])
    amount = int(request.POST['amount'])
    if user.wallet.money < amount:
        return JsonResponse({"error": "Insufficient funds"}, status=400)

    user.wallet.money -= amount
    user.wallet.save()
    return redirect("/wallet?transaction=withdraw")


def add(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = User.objects.get(uuid=request.COOKIES['user-identity'])
    amount = int(request.POST['amount'])
    user.wallet.money += amount
    user.wallet.save()
    return redirect("/wallet?transaction=add")


def not_found_404(request):
    return render(request, "404.html")
