from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("book/<slug:slug>/", views.book_style, name="book_style"),
    path("book/thank-you/<int:pk>/", views.thank_you, name="thank_you"),
]
