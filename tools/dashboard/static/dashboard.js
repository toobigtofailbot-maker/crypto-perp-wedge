const sections = Array.from(document.querySelectorAll(".page-section"));
const links = Array.from(document.querySelectorAll(".sidebar a"));
const filters = Array.from(document.querySelectorAll("[data-filter-target]"));

function markActive() {
  const current = sections.findLast((section) => section.getBoundingClientRect().top <= 96);
  const activeId = current ? `#${current.id}` : "#overview";
  for (const link of links) {
    link.classList.toggle("active", link.getAttribute("href") === activeId);
  }
}

document.addEventListener("scroll", markActive, { passive: true });
markActive();

for (const filter of filters) {
  const panel = filter.closest(".panel");
  const rows = panel ? Array.from(panel.querySelectorAll(".filter-row")) : [];
  filter.addEventListener("input", () => {
    const query = filter.value.trim().toLowerCase();
    for (const row of rows) {
      row.classList.toggle("is-hidden", query !== "" && !row.textContent.toLowerCase().includes(query));
    }
  });
}
