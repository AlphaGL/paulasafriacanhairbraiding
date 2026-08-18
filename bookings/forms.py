from datetime import date

from django import forms

from .models import Booking, BusinessSettings

WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "customer_name",
            "customer_email",
            "customer_phone",
            "location_type",
            "customer_address",
            "requested_date",
            "requested_time",
            "notes",
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "customer_email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "customer_phone": forms.TextInput(attrs={"placeholder": "(555) 555-5555"}),
            "location_type": forms.RadioSelect,
            "customer_address": forms.TextInput(
                attrs={"placeholder": "Street address, city, zip"}
            ),
            "requested_date": forms.DateInput(attrs={"type": "date"}),
            "requested_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Any special requests? (optional)"}
            ),
        }

    def clean_requested_date(self):
        requested_date = self.cleaned_data["requested_date"]
        if requested_date < date.today():
            raise forms.ValidationError("Please choose a date in the future.")

        business = BusinessSettings.load()
        if requested_date.weekday() in business.days_closed_list:
            closed_names = ", ".join(
                WEEKDAY_NAMES[d] for d in business.days_closed_list
            )
            raise forms.ValidationError(
                f"Paula isn't available on this day ({closed_names}). Please pick another date."
            )
        return requested_date

    def clean(self):
        cleaned_data = super().clean()
        location_type = cleaned_data.get("location_type")
        customer_address = cleaned_data.get("customer_address")
        if location_type == "mobile" and not customer_address:
            self.add_error(
                "customer_address",
                "Please enter your address so Paula knows where to come.",
            )
        return cleaned_data
