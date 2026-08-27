from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from styles.models import HairstyleService

WEEKDAY_CHOICES = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]


class BusinessSettings(models.Model):
    """Single-row model holding Paulette's editable business info."""

    business_name = models.CharField(max_length=150, default="Paulette's African Hair Braiding")
    address_line = models.CharField(max_length=255, default="4203 Trio Avenue")
    city = models.CharField(max_length=100, default="Louisville")
    state = models.CharField(max_length=50, default="KY")
    zip_code = models.CharField(max_length=20, default="40219")
    email = models.EmailField(default="Pauletteagbeti@gmail.com")
    phone = models.CharField(max_length=30, blank=True)

    travel_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("25.00"),
        help_text="Flat fee added to bookings where Paulette travels to the customer.",
    )

    business_hours_note = models.CharField(
        max_length=255,
        blank=True,
        default="Mon-Sat, 9:00 AM - 6:00 PM",
        help_text="Shown to customers on the site (free text).",
    )
    days_closed = models.CharField(
        max_length=50,
        blank=True,
        default="6",
        help_text="Comma-separated weekday numbers she's closed (0=Mon ... 6=Sun). Default: Sunday.",
    )

    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "business settings"

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def full_address(self):
        return f"{self.address_line}, {self.city}, {self.state} {self.zip_code}"

    @property
    def days_closed_list(self):
        if not self.days_closed:
            return []
        return [int(d) for d in self.days_closed.split(",") if d.strip().isdigit()]


class Booking(models.Model):
    class LocationType(models.TextChoices):
        SALON = "salon", "At Paulette's location"
        MOBILE = "mobile", "Paulette comes to me"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)

    hairstyle = models.ForeignKey(
        HairstyleService, related_name="bookings", on_delete=models.PROTECT
    )

    location_type = models.CharField(max_length=10, choices=LocationType.choices)
    customer_address = models.CharField(max_length=255, blank=True)

    requested_date = models.DateField()
    requested_time = models.TimeField()

    salon_price_snapshot = models.DecimalField(max_digits=7, decimal_places=2)
    travel_fee_snapshot = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))

    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} - {self.hairstyle.name} on {self.requested_date}"

    def clean(self):
        if self.location_type == self.LocationType.MOBILE and not self.customer_address:
            raise ValidationError(
                {"customer_address": "Address is required when Paulette is traveling to you."}
            )

    @property
    def total_price(self):
        return self.salon_price_snapshot + self.travel_fee_snapshot
