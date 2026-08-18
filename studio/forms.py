from django import forms

from bookings.models import Booking, BusinessSettings
from styles.models import Category, GalleryImage, HairstyleService


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "sort_order"]


class HairstyleForm(forms.ModelForm):
    class Meta:
        model = HairstyleService
        fields = [
            "name",
            "category",
            "description",
            "salon_price",
            "duration_estimate",
            "cover_image",
            "is_active",
            "sort_order",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["image", "caption", "sort_order"]


class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = [
            "business_name",
            "address_line",
            "city",
            "state",
            "zip_code",
            "email",
            "phone",
            "travel_fee",
            "business_hours_note",
            "days_closed",
            "instagram_url",
            "facebook_url",
        ]
        widgets = {
            "days_closed": forms.TextInput(
                attrs={"placeholder": "e.g. 6 for Sunday, or 5,6 for Sat+Sun"}
            ),
        }


class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["status"]
