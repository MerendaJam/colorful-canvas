/* ============================================================
   COLORFUL CANVAS — Main JavaScript
   Ultra-lightweight, no dependencies
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* --- Mobile Nav Toggle --- */
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      toggle.setAttribute('aria-expanded', isOpen);
    });
    // Close nav on link click (mobile)
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
      });
    });
  }

  /* --- Active Nav Link --- */
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  /* --- Scroll Fade-Up Animation --- */
  const fadeEls = document.querySelectorAll('.fade-up');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    fadeEls.forEach(function (el) { el.classList.add('visible'); });
  }

  /* --- Booking Form Validation & Feedback --- */
  const bookingForm = document.getElementById('booking-form');
  if (bookingForm) {
    bookingForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = bookingForm.querySelector('.form-submit');
      const original = btn.innerHTML;
      btn.innerHTML = '⏳ Sending…';
      btn.disabled = true;

      const formData = new FormData(bookingForm);
      fetch('/book', {
        method: 'POST',
        body: formData
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        showAlert(data.success ? 'success' : 'error',
          data.success
            ? '🎉 Thank you! We received your booking request and will reply within 24 hours.'
            : '❌ Something went wrong. Please email us directly.');
        if (data.success) bookingForm.reset();
      })
      .catch(function () {
        showAlert('error', '❌ Network error. Please try again or email us directly.');
      })
      .finally(function () {
        btn.innerHTML = original;
        btn.disabled = false;
      });
    });
  }

  function showAlert(type, message) {
    const existing = document.querySelector('.form-alert');
    if (existing) existing.remove();
    const alert = document.createElement('div');
    alert.className = 'alert alert-' + type + ' form-alert';
    alert.textContent = message;
    const form = document.getElementById('booking-form');
    if (form) form.insertAdjacentElement('beforebegin', alert);
    alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(function () { alert.remove(); }, 8000);
  }

  /* --- Upload Area Click-to-Browse (Admin) --- */
  const uploadArea = document.querySelector('.upload-area');
  const fileInput = document.getElementById('media-file');
  if (uploadArea && fileInput) {
    uploadArea.addEventListener('click', function () { fileInput.click(); });
    fileInput.addEventListener('change', function () {
      const name = fileInput.files[0] ? fileInput.files[0].name : 'No file selected';
      uploadArea.querySelector('p').textContent = '📎 ' + name;
    });
    uploadArea.addEventListener('dragover', function (e) {
      e.preventDefault();
      uploadArea.style.borderColor = 'var(--raspberry)';
    });
    uploadArea.addEventListener('dragleave', function () {
      uploadArea.style.borderColor = '';
    });
    uploadArea.addEventListener('drop', function (e) {
      e.preventDefault();
      uploadArea.style.borderColor = '';
      const files = e.dataTransfer.files;
      if (files.length) {
        fileInput.files = files;
        uploadArea.querySelector('p').textContent = '📎 ' + files[0].name;
      }
    });
  }

  /* --- Smooth scroll for anchor links --- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
