// BookNest - client-side interaction & validation.
// NOTE: the server validates everything again; this is only for fast feedback.
document.addEventListener("DOMContentLoaded", () => {
  // Dark / light theme toggle (choice is remembered in localStorage)
  const root = document.documentElement, themeBtn = document.getElementById("themeToggle");
  const syncTheme = () => {
    const dark = root.getAttribute("data-theme") === "dark";
    if (themeBtn) { themeBtn.textContent = dark ? "☀️" : "🌙"; themeBtn.setAttribute("aria-pressed", dark); }
  };
  syncTheme();
  if (themeBtn) themeBtn.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) { /* storage blocked */ }
    syncTheme();
  });

  // Mobile navigation
  const toggle = document.getElementById("navToggle");
  const nav = document.getElementById("mainNav");
  if (toggle) toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open);
  });

  // Dismissible flash messages
  document.querySelectorAll(".flash").forEach(f => {
    f.querySelector(".flash-close").addEventListener("click", () => f.remove());
    if (f.classList.contains("success")) setTimeout(() => f.remove(), 5000);
  });

  // Confirm before deleting
  document.querySelectorAll("form.js-confirm").forEach(f =>
    f.addEventListener("submit", e => { if (!confirm(f.dataset.msg || "Are you sure?")) e.preventDefault(); }));

  // Form validation (rules come from data-* attributes)
  const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  function check(field, form) {
    const v = field.value.trim();
    const d = field.dataset;
    if ("required" in d && !v) return "This field is required.";
    if (!v) return "";
    if (d.min && v.length < +d.min) return `Must be at least ${d.min} characters.`;
    if ("email" in d && !EMAIL.test(v)) return "Enter a valid email address.";
    if ("password" in d && (field.value.length < 8 || !/[A-Za-z]/.test(field.value) || !/\d/.test(field.value)))
      return "Use 8+ characters with a letter and a number.";
    if (d.match && field.value !== form.elements[d.match].value) return "Passwords do not match.";
    return "";
  }
  function show(field, msg) {
    let el = field.parentElement.querySelector(".error-msg");
    if (!el) { el = document.createElement("span"); el.className = "error-msg"; field.parentElement.appendChild(el); }
    el.textContent = msg;
    field.classList.toggle("invalid", !!msg);
  }
  document.querySelectorAll("form[data-validate]").forEach(form => {
    const fields = form.querySelectorAll("input, select, textarea");
    fields.forEach(f => f.addEventListener("blur", () => show(f, check(f, form))));
    form.addEventListener("submit", e => {
      let bad = null;
      fields.forEach(f => { const m = check(f, form); show(f, m); if (m && !bad) bad = f; });
      if (bad) { e.preventDefault(); bad.focus(); }
    });
  });

  // Password strength meter
  const pw = document.getElementById("password"), meter = document.getElementById("strength");
  if (pw && meter) pw.addEventListener("input", () => {
    const v = pw.value;
    const score = (v.length >= 8) + /[a-z]/.test(v) + /[A-Z]/.test(v) + /\d/.test(v) + /[^A-Za-z0-9]/.test(v);
    const labels = ["", "Weak", "Weak", "Fair", "Good", "Strong"];
    meter.textContent = v ? "Strength: " + labels[score] : "";
    meter.style.color = score >= 4 ? "#1f7a4d" : score === 3 ? "#b57a00" : "#b3261e";
  });

  // Image preview
  const img = document.getElementById("image"), prev = document.getElementById("preview");
  if (img && prev) img.addEventListener("change", () => {
    const file = img.files[0];
    if (file && file.size > 2 * 1024 * 1024) { alert("Image must be 2 MB or smaller."); img.value = ""; prev.hidden = true; return; }
    if (file) { prev.src = URL.createObjectURL(file); prev.hidden = false; } else prev.hidden = true;
  });
});
