from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class HairstyleService(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    category = models.ForeignKey(
        Category, related_name="styles", on_delete=models.PROTECT
    )
    description = models.TextField(blank=True)
    salon_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Price when the customer comes to Paula's location.",
    )
    duration_estimate = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g. "4-6 hours"',
    )
    cover_image = models.ImageField(
        upload_to="styles/covers/", blank=True, null=True
    )
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide this style from the public site."
    )
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while HairstyleService.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("styles:detail", kwargs={"slug": self.slug})

    def mobile_price(self, travel_fee):
        return self.salon_price + travel_fee


class GalleryImage(models.Model):
    hairstyle = models.ForeignKey(
        HairstyleService, related_name="gallery_images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="styles/gallery/")
    caption = models.CharField(max_length=150, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.hairstyle.name} photo #{self.pk}"
