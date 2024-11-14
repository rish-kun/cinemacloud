from django.contrib.auth import logout
from main.models import User
from django.shortcuts import redirect, render
# Create your views here.


def login(request):
    print(request.user)
    return render(request, 'oauth/login.html')


def logout_view(request):
    logout(request)
    return redirect('oauth:login')


def profile(request):
    user = request.user
    print(user.email)
    name = user.first_name+" "+user.last_name
    email = user.email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create(
            email=email, name=name, google_account=True, email_verified=True)
        user.create_wallet()
        user.save()
        resp = redirect("main:index")
        resp.set_cookie("user-identity", user.uuid)
        logout(request)
        return resp
    resp = redirect("main:index")
    resp.set_cookie("user-identity", user.uuid)
    return resp
