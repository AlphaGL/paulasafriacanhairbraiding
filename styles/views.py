from django.shortcuts import get_object_or_404, render

from bookings.models import BusinessSettings

from .models import Category, HairstyleService


def style_list(request):
    categories = Category.objects.prefetch_related("styles").all()
    active_styles = HairstyleService.objects.filter(is_active=True).select_related("category")
    business = BusinessSettings.load()
    return render(
        request,
        "styles/style_list.html",
        {
            "categories": categories,
            "styles": active_styles,
            "business": business,
        },
    )


def style_detail(request, slug):
    hairstyle = get_object_or_404(
        HairstyleService.objects.select_related("category").prefetch_related("gallery_images"),
        slug=slug,
        is_active=True,
    )
    business = BusinessSettings.load()
    mobile_price = hairstyle.salon_price + business.travel_fee
    return render(
        request,
        "styles/style_detail.html",
        {
            "hairstyle": hairstyle,
            "business": business,
            "mobile_price": mobile_price,
        },
    )
