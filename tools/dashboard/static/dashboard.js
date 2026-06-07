const sections = Array.from(document.querySelectorAll(".page-section"));
const links = Array.from(document.querySelectorAll(".sidebar a"));

function markActive() {
  const current = sections.findLast((section) => section.getBoundingClientRect().top <= 96);
  const activeId = current ? `#${current.id}` : "#overview";
  for (const link of links) {
    link.classList.toggle("active", link.getAttribute("href") === activeId);
  }
}

document.addEventListener("scroll", markActive, { passive: true });
markActive();
