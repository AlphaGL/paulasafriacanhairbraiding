from django.core.management.base import BaseCommand

from bookings.models import BusinessSettings
from styles.models import Category

STARTER_CATEGORIES = [
    "Cornrows",
    "Box Braids",
    "Feed-in Braids",
    "Goddess Braids",
    "Senegalese Twists",
]


class Command(BaseCommand):
    help = "Seeds business settings (Paula's info) and starter style categories."

    def handle(self, *args, **options):
        business = BusinessSettings.load()
        business.business_name = "Paula's African Hair Braiding"
        business.address_line = "4203 Trio Avenue"
        business.city = "Louisville"
        business.state = "KY"
        business.zip_code = "40219"
        business.email = "Pauletteagbeti@gmail.com"
        business.save()
        self.stdout.write(self.style.SUCCESS("Business settings ready."))

        for i, name in enumerate(STARTER_CATEGORIES):
            category, created = Category.objects.get_or_create(
                name=name, defaults={"sort_order": i}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))
            else:
                self.stdout.write(f"Category already exists: {name}")

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
