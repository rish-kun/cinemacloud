from django.urls import path
from .views import *
app_name = "main"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login", LoginView.as_view(), name="login"),
    path("signup", SignupView.as_view(), name="signup"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("show/<str:show_id>", ShowView.as_view(), name="show"),
    path("book/", BookView.as_view(), name="book"),
    path("ticket/<uuid:ticket_id>/cancel/",
         CancelTicketView.as_view(), name="cancel_ticket"),
    path("confirm/<uuid:transaction_id>/",
         ConfirmTransactionView.as_view(), name="confirm_transaction"),
    path("ticket/<uuid:ticket_id>/food/",
         FoodOrderView.as_view(), name="order_food"),
    path("wallet", wallet, name="wallet"),
    path("withdraw", withdraw, name="withdraw"),
    path("add", add, name="add"),
    path("404", not_found_404, name="404"),
    path("account", AccountView.as_view(), name="account"),
    path("tickets", TicketView.as_view(), name="tickets"),
    path("movies", movies, name="movies"),
    path("shows/<uuid:movie_id>", shows, name="shows"),
    path("ticket/<uuid:ticket_id>", ticket, name="ticket"),
    path("transaction/<uuid:transaction_id>", transaction, name="transaction"),
    path("transactions", transactions, name="transactions"),
    path("password_change", PasswordChangeView.as_view(), name="password_change"),
    path("account_edit", AccountEditView.as_view(), name="account_edit"),
    path("search/", search_shows, name="search"),
    path("theatres", theatres, name="theatres"),
    path("theatre/<uuid:theatre_id>", theatre, name="theatre"),
    path("search_movies/", search_movies, name="search_movies"),
    path("verification_email", verification_email, name="verification_email"),
    path("verify/<uuid:query_id>/<uuid:user_id>",
         verify_email, name="verify_email"),

]
