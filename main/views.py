from django.shortcuts import render, redirect
from django.views import View
from .models import User, Ticket, Transaction, Movie
import bcrypt


class IndexView(View):
    def get(self, request):
        try:
            request.COOKIES['user-identity']
        except KeyError:
            return redirect("main:login")
        mov_list = Movie.objects.all()
        for z in mov_list:
            print(z.id)
        return render(request, "main/index.html", context={"user": User.objects.get(uuid=request.COOKIES['user-identity']), "movies": mov_list})


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
