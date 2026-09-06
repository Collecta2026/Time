// Mobile sidebar toggle
document.addEventListener("click", function (e) {
  if (e.target.closest(".menu-btn")) {
    document.querySelector(".sidebar").classList.toggle("open");
  }
});

// Confirm before any form marked data-confirm submits
document.addEventListener("submit", function (e) {
  const msg = e.target.getAttribute("data-confirm");
  if (msg && !window.confirm(msg)) e.preventDefault();
});

// Grade/spine live headroom helper on employee form
function updateSpine(sel) {
  const opt = sel.options[sel.selectedIndex];
  const salaryField = document.getElementById("basic_hint");
  if (opt && opt.dataset.salary && salaryField) {
    salaryField.textContent = opt.dataset.salary;
  }
}
