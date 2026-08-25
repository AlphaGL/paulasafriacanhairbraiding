from django.urls import path

from . import views

app_name = "studio"

urlpatterns = [
    path("login/", views.StudioLoginView.as_view(), name="login"),
    path("logout/", views.StudioLogoutView.as_view(), name="logout"),
    path("password/", views.change_password, name="change_password"),
    path("", views.dashboard, name="dashboard"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("styles/", views.style_list, name="style_list"),
    path("styles/new/", views.style_create, name="style_create"),
    path("styles/<int:pk>/edit/", views.style_edit, name="style_edit"),
    path("styles/<int:pk>/delete/", views.style_delete, name="style_delete"),
    path("styles/<int:pk>/gallery/add/", views.gallery_image_add, name="gallery_image_add"),
    path(
        "styles/<int:pk>/gallery/<int:image_pk>/delete/",
        views.gallery_image_delete,
        name="gallery_image_delete",
    ),
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("settings/", views.business_settings, name="business_settings"),
]
