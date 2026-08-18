from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from styles.models import HairstyleService

from .emails import send_booking_emails
from .forms import BookingForm
from .models import BusinessSettings


def book_style(request, slug):
    hairstyle = get_object_or_404(HairstyleService, slug=slug, is_active=True)
    business = BusinessSettings.load()

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.hairstyle = hairstyle
            booking.salon_price_snapshot = hairstyle.salon_price
            booking.travel_fee_snapshot = (
                business.travel_fee if booking.location_type == "mobile" else 0
            )
            booking.save()
            send_booking_emails(booking, business)
            return redirect(reverse("bookings:thank_you", args=[booking.pk]))
    else:
        form = BookingForm()

    mobile_price = hairstyle.salon_price + business.travel_fee

    return render(
        request,
        "bookings/booking_form.html",
        {
            "form": form,
            "hairstyle": hairstyle,
            "business": business,
            "mobile_price": mobile_price,
        },
    )


def thank_you(request, pk):
    from .models import Booking

    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "bookings/thank_you.html", {"booking": booking})
