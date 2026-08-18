document.addEventListener("DOMContentLoaded", function () {
  // Mobile nav toggle
  var navToggle = document.getElementById("navToggle");
  var siteNav = document.getElementById("siteNav");
  if (navToggle && siteNav) {
    navToggle.addEventListener("click", function () {
      var isOpen = siteNav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", isOpen);
    });
    siteNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        siteNav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Header gains a stronger shadow once the page scrolls
  var header = document.getElementById("siteHeader");

  // Scroll-linked color wash: the page tint and header hue drift as you scroll
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ticking = false;
  function onScrollEffects() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 12);
    if (!reduceMotion) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      var progress = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
      document.documentElement.style.setProperty("--scroll-progress", progress.toFixed(4));
      document.body.style.backgroundPosition = (progress * 120) + "% " + (50 + progress * 50) + "%";
    }
    ticking = false;
  }
  window.addEventListener(
    "scroll",
    function () {
      if (!ticking) {
        window.requestAnimationFrame(onScrollEffects);
        ticking = true;
      }
    },
    { passive: true }
  );
  onScrollEffects();

  // Scroll-reveal: elements animate in AND out every time they cross the viewport,
  // with images getting a sharper clip-path "wipe" instead of a plain fade.
  // Content only gets hidden in the first place once we know JS is actually
  // running (see the .js-ready gate in site.css) — and even then, a short
  // timeout below force-reveals anything the observer somehow misses, so
  // nothing can end up permanently invisible.
  var revealEls = document.querySelectorAll("[data-reveal]");
  if (revealEls.length) {
    document.documentElement.classList.add("js-ready");
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            entry.target.classList.toggle("is-visible", entry.isIntersecting);
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -10% 0px" }
      );
      revealEls.forEach(function (el) { observer.observe(el); });
    } else {
      revealEls.forEach(function (el) { el.classList.add("is-visible"); });
    }
    window.setTimeout(function () {
      revealEls.forEach(function (el) { el.classList.add("is-visible"); });
    }, 2500);
  }

  // Category filter on the styles grid
  var pills = document.querySelectorAll(".category-pill");
  var cards = document.querySelectorAll("[data-category]");
  pills.forEach(function (pill) {
    pill.addEventListener("click", function () {
      pills.forEach(function (p) { p.classList.remove("active"); });
      pill.classList.add("active");
      var filter = pill.getAttribute("data-filter");
      cards.forEach(function (card) {
        var show = filter === "all" || card.getAttribute("data-category") === filter;
        var innerImg = card.querySelector(".reveal-img");
        if (show) {
          card.style.display = "";
          card.classList.remove("is-visible");
          if (innerImg) innerImg.classList.remove("is-visible");
          requestAnimationFrame(function () {
            card.classList.add("is-visible");
            if (innerImg) innerImg.classList.add("is-visible");
          });
        } else {
          card.style.display = "none";
        }
      });
    });
  });

  // Style detail gallery: thumbnail switching + lightbox
  var mainImage = document.getElementById("styleMainImage");
  var thumbs = document.querySelectorAll(".style-gallery-thumbs img");
  var galleryTrigger = document.getElementById("styleGalleryTrigger");
  var lightbox = document.getElementById("lightbox");
  var lightboxImage = document.getElementById("lightboxImage");
  var lightboxClose = document.getElementById("lightboxClose");

  function setMainImage(src) {
    if (!mainImage || !src) return;
    mainImage.style.opacity = "0";
    window.setTimeout(function () {
      mainImage.src = src;
      mainImage.style.opacity = "1";
    }, 120);
  }

  thumbs.forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      setMainImage(thumb.getAttribute("data-full") || thumb.src);
      thumbs.forEach(function (t) { t.classList.remove("active"); });
      thumb.classList.add("active");
    });
  });

  function openLightbox(src) {
    if (!lightbox || !lightboxImage || !src) return;
    lightboxImage.src = src;
    lightbox.classList.add("open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove("open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  if (galleryTrigger) {
    galleryTrigger.addEventListener("click", function () {
      openLightbox(mainImage ? mainImage.src : null);
    });
  }
  if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
  if (lightbox) {
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) closeLightbox();
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeLightbox();
  });

  // Hero showcase: crossfades through style photos on a timer. Independent of
  // scroll/IntersectionObserver entirely, so it's always running once loaded.
  var showcaseImgs = document.querySelectorAll(".hero-showcase-img");
  var showcaseDots = document.querySelectorAll(".hero-dot");
  if (showcaseImgs.length > 1) {
    var showcaseIndex = 0;
    var showcaseTimer = null;
    function showSlide(i) {
      showcaseImgs.forEach(function (img, idx) { img.classList.toggle("active", idx === i); });
      showcaseDots.forEach(function (dot, idx) { dot.classList.toggle("active", idx === i); });
      showcaseIndex = i;
    }
    function startShowcase() {
      showcaseTimer = window.setInterval(function () {
        showSlide((showcaseIndex + 1) % showcaseImgs.length);
      }, 3200);
    }
    startShowcase();
    showcaseDots.forEach(function (dot, idx) {
      dot.addEventListener("click", function () {
        window.clearInterval(showcaseTimer);
        showSlide(idx);
        startShowcase();
      });
    });
  }

  // Gentle 3D tilt on hover for style cards + hero image (fancy, but subtle)
  var tiltEls = document.querySelectorAll(".style-card, .hero-image");
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    tiltEls.forEach(function (el) {
      var maxTilt = el.classList.contains("hero-image") ? 6 : 8;
      el.addEventListener("mousemove", function (e) {
        var rect = el.getBoundingClientRect();
        var x = (e.clientX - rect.left) / rect.width - 0.5;
        var y = (e.clientY - rect.top) / rect.height - 0.5;
        var rotateY = x * maxTilt * 2;
        var rotateX = y * -maxTilt * 2;
        el.style.transform = "translateY(-6px) rotateX(" + rotateX + "deg) rotateY(" + rotateY + "deg)";
        el.classList.add("tilt-active");
      });
      el.addEventListener("mouseleave", function () {
        el.style.transform = "";
        el.classList.remove("tilt-active");
      });
    });
  }

  // Booking form: toggle address field + live price based on location type
  var locationInputs = document.querySelectorAll('input[name="location_type"]');
  var addressGroup = document.getElementById("addressGroup");
  var priceDisplay = document.getElementById("livePrice");
  var salonPrice = priceDisplay ? parseFloat(priceDisplay.getAttribute("data-salon-price")) : 0;
  var mobilePrice = priceDisplay ? parseFloat(priceDisplay.getAttribute("data-mobile-price")) : 0;

  function updateBookingUI() {
    var selected = document.querySelector('input[name="location_type"]:checked');
    if (!selected) return;
    var isMobile = selected.value === "mobile";

    if (addressGroup) {
      if (isMobile) {
        addressGroup.classList.add("field-open");
      } else {
        addressGroup.classList.remove("field-open");
      }
    }

    if (priceDisplay) {
      var newValue = "$" + (isMobile ? mobilePrice : salonPrice).toFixed(2);
      if (priceDisplay.textContent !== newValue) {
        priceDisplay.textContent = newValue;
        priceDisplay.classList.remove("price-pulse");
        void priceDisplay.offsetWidth;
        priceDisplay.classList.add("price-pulse");
      }
    }

    document.querySelectorAll(".radio-option").forEach(function (opt) {
      var input = opt.querySelector('input[name="location_type"]');
      if (input) opt.classList.toggle("checked", input.checked);
    });
  }

  if (locationInputs.length) {
    locationInputs.forEach(function (input) {
      input.addEventListener("change", updateBookingUI);
    });
    if (addressGroup) addressGroup.classList.add("field-init");
    updateBookingUI();
  }
});
