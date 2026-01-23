/*
  DRIVER LOGIN — DJANGO READY
  - Bootstrap validation
  - Secure POST with CSRF
  - Redirect to driver dashboard
*/

(function () {

  const form = document.getElementById('driverForm');
  if (!form) return;

  // =========================
  // Get CSRF token (Django)
  // =========================
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  // =========================
  // Submit handler
  // =========================
  form.addEventListener('submit', function (e) {

    // Bootstrap validation
    if (!form.checkValidity()) {
      e.preventDefault();
      e.stopPropagation();
      form.classList.add('was-validated');
      return;
    }

    e.preventDefault();

    const formData = new FormData(form);

    fetch('/driver/auth/driver/login/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Login failed');
      }
      return response.json();
    })
    .then(data => {

      /*
        Expected Django response:
        {
          "success": true,
          "role": "driver"
        }
      */

      if (data.success && data.role === 'driver') {
        window.location.href = '/driver/dashboard/';
      } else {
        alert('Accès non autorisé');
      }

    })
    .catch(error => {
      console.error(error);
      alert('Email ou mot de passe incorrect');
    });

  });

})();
