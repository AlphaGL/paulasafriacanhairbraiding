from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_booking_emails(booking, business):
    context = {"booking": booking, "business": business, "site_url": settings.SITE_URL}

    owner_subject = f"New booking request: {booking.hairstyle.name} on {booking.requested_date}"
    owner_text = render_to_string("bookings/email/owner_notification.txt", context)
    owner_html = render_to_string("bookings/email/owner_notification.html", context)
    owner_message = EmailMultiAlternatives(
        subject=owner_subject,
        body=owner_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.BUSINESS_NOTIFICATION_EMAIL],
        reply_to=[booking.customer_email],
    )
    owner_message.attach_alternative(owner_html, "text/html")
    owner_message.send(fail_silently=False)

    customer_subject = f"Your booking request with {business.business_name}"
    customer_text = render_to_string("bookings/email/customer_confirmation.txt", context)
    customer_html = render_to_string("bookings/email/customer_confirmation.html", context)
    customer_message = EmailMultiAlternatives(
        subject=customer_subject,
        body=customer_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.customer_email],
        reply_to=[business.email],
    )
    customer_message.attach_alternative(customer_html, "text/html")
    customer_message.send(fail_silently=False)
