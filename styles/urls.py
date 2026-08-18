from django.urls import path

from . import views

app_name = "styles"

urlpatterns = [
    path("", views.style_list, name="list"),
    path("<slug:slug>/", views.style_detail, name="detail"),
]
