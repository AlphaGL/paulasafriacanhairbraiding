document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("studioNavToggle");
  var sidebar = document.getElementById("studioSidebar");
  var backdrop = document.getElementById("studioSidebarBackdrop");

  if (!toggle || !sidebar || !backdrop) return;

  function openMenu() {
    sidebar.classList.add("open");
    backdrop.classList.add("open");
    toggle.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeMenu() {
    sidebar.classList.remove("open");
    backdrop.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  toggle.addEventListener("click", function () {
    if (sidebar.classList.contains("open")) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  backdrop.addEventListener("click", closeMenu);

  sidebar.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenu();
  });

  // Collapsing back to desktop width shouldn't leave the drawer state stuck open
  window.addEventListener("resize", function () {
    if (window.innerWidth > 860) closeMenu();
  });
});
