from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_booking_emails(booking, business):
    context = {"booking": booking, "business": business}

    owner_subject = f"New booking request: {booking.hairstyle.name} on {booking.requested_date}"
    owner_body = render_to_string("bookings/email/owner_notification.txt", context)
    EmailMessage(
        subject=owner_subject,
        body=owner_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.BUSINESS_NOTIFICATION_EMAIL],
        reply_to=[booking.customer_email],
    ).send(fail_silently=False)

    customer_subject = f"Your booking request with {business.business_name}"
    customer_body = render_to_string("bookings/email/customer_confirmation.txt", context)
    EmailMessage(
        subject=customer_subject,
        body=customer_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.customer_email],
        reply_to=[business.email],
    ).send(fail_silently=False)
