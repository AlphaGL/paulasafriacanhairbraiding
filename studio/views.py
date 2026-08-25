from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from bookings.models import Booking, BusinessSettings
from styles.models import Category, GalleryImage, HairstyleService

from .forms import (
    BookingStatusForm,
    BusinessSettingsForm,
    CategoryForm,
    GalleryImageForm,
    HairstyleForm,
)


class StudioLoginView(LoginView):
    template_name = "studio/login.html"
    redirect_authenticated_user = True


class StudioLogoutView(LogoutView):
    next_page = reverse_lazy("studio:login")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Changing the password invalidates the old session hash — without
            # this the admin would be immediately logged out by their own change.
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated.")
            return redirect("studio:dashboard")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "studio/change_password.html", {"form": form})


@login_required
def dashboard(request):
    today = date.today()
    week_end = today + timedelta(days=7)

    pending_count = Booking.objects.filter(status=Booking.Status.PENDING).count()
    upcoming_bookings = Booking.objects.filter(
        requested_date__gte=today, requested_date__lte=week_end
    ).exclude(status=Booking.Status.CANCELLED).select_related("hairstyle")
    style_count = HairstyleService.objects.count()
    active_style_count = HairstyleService.objects.filter(is_active=True).count()

    return render(
        request,
        "studio/dashboard.html",
        {
            "pending_count": pending_count,
            "upcoming_bookings": upcoming_bookings,
            "style_count": style_count,
            "active_style_count": active_style_count,
        },
    )


# --- Bookings ---------------------------------------------------------------

@login_required
def booking_list(request):
    bookings = Booking.objects.select_related("hairstyle").all()

    status_filter = request.GET.get("status", "")
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    date_filter = request.GET.get("date", "")
    if date_filter:
        bookings = bookings.filter(requested_date=date_filter)

    date_counts = {}
    for b in bookings:
        date_counts[b.requested_date] = date_counts.get(b.requested_date, 0) + 1
    overlap_dates = {d for d, count in date_counts.items() if count > 1}

    return render(
        request,
        "studio/booking_list.html",
        {
            "bookings": bookings,
            "status_choices": Booking.Status.choices,
            "current_status": status_filter,
            "current_date": date_filter,
            "overlap_dates": overlap_dates,
        },
    )


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("hairstyle"), pk=pk)

    if request.method == "POST":
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking status updated.")
            return redirect("studio:booking_detail", pk=booking.pk)
    else:
        form = BookingStatusForm(instance=booking)

    return render(
        request, "studio/booking_detail.html", {"booking": booking, "form": form}
    )


# --- Styles (CRUD) -----------------------------------------------------------

@login_required
def style_list(request):
    hairstyles = HairstyleService.objects.select_related("category").all()
    return render(request, "studio/style_list.html", {"hairstyles": hairstyles})


@login_required
def style_create(request):
    if request.method == "POST":
        form = HairstyleForm(request.POST, request.FILES)
        if form.is_valid():
            hairstyle = form.save()
            messages.success(request, f'"{hairstyle.name}" was created.')
            return redirect("studio:style_edit", pk=hairstyle.pk)
    else:
        form = HairstyleForm()
    return render(
        request, "studio/style_form.html", {"form": form, "is_new": True}
    )


@login_required
def style_edit(request, pk):
    hairstyle = get_object_or_404(HairstyleService, pk=pk)

    if request.method == "POST":
        form = HairstyleForm(request.POST, request.FILES, instance=hairstyle)
        if form.is_valid():
            form.save()
            messages.success(request, "Style updated.")
            return redirect("studio:style_edit", pk=hairstyle.pk)
    else:
        form = HairstyleForm(instance=hairstyle)

    gallery_form = GalleryImageForm()

    return render(
        request,
        "studio/style_form.html",
        {
            "form": form,
            "hairstyle": hairstyle,
            "is_new": False,
            "gallery_images": hairstyle.gallery_images.all(),
            "gallery_form": gallery_form,
        },
    )


@login_required
def style_delete(request, pk):
    hairstyle = get_object_or_404(HairstyleService, pk=pk)
    if request.method == "POST":
        name = hairstyle.name
        hairstyle.delete()
        messages.success(request, f'"{name}" was deleted.')
        return redirect("studio:style_list")
    return render(request, "studio/confirm_delete.html", {"object": hairstyle, "type_label": "style"})


@login_required
def gallery_image_add(request, pk):
    hairstyle = get_object_or_404(HairstyleService, pk=pk)
    if request.method == "POST":
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.hairstyle = hairstyle
            image.save()
            messages.success(request, "Photo added.")
    return redirect("studio:style_edit", pk=hairstyle.pk)


@login_required
def gallery_image_delete(request, pk, image_pk):
    image = get_object_or_404(GalleryImage, pk=image_pk, hairstyle_id=pk)
    if request.method == "POST":
        image.delete()
        messages.success(request, "Photo removed.")
    return redirect("studio:style_edit", pk=pk)


# --- Categories (CRUD) --------------------------------------------------------

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "studio/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created.")
            return redirect("studio:category_list")
    else:
        form = CategoryForm()
    return render(request, "studio/category_form.html", {"form": form, "is_new": True})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("studio:category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "studio/category_form.html", {"form": form, "is_new": False, "category": category})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        if category.styles.exists():
            messages.error(
                request,
                "Can't delete a category that still has styles in it. Move or delete those styles first.",
            )
            return redirect("studio:category_list")
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("studio:category_list")
    return render(request, "studio/confirm_delete.html", {"object": category, "type_label": "category"})


# --- Business settings -------------------------------------------------------

@login_required
def business_settings(request):
    settings_obj = BusinessSettings.load()
    if request.method == "POST":
        form = BusinessSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Business settings updated.")
            return redirect("studio:business_settings")
    else:
        form = BusinessSettingsForm(instance=settings_obj)
    return render(request, "studio/business_settings.html", {"form": form})
