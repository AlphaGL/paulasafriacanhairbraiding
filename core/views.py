from django.shortcuts import render

from bookings.models import BusinessSettings
from styles.models import Category, HairstyleService


def home(request):
    business = BusinessSettings.load()
    active_styles = HairstyleService.objects.filter(is_active=True).select_related(
        "category"
    )
    featured_styles = active_styles[:5]
    showcase_styles = [style for style in active_styles if style.cover_image][:8]
    categories = Category.objects.all()
    return render(
        request,
        "core/home.html",
        {
            "business": business,
            "featured_styles": featured_styles,
            "showcase_styles": showcase_styles,
            "categories": categories,
        },
    )


def about(request):
    business = BusinessSettings.load()
    return render(request, "core/about.html", {"business": business})
