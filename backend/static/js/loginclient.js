/*
  CLIENT LOGIN — DJANGO READY
  - Bootstrap validation
  - Secure POST (CSRF)
  - Redirect to client dashboard
*/

(function () {

  const form = document.getElementById('clientForm');
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

    fetch('/client/auth/client/login/', {
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
          "role": "client"
        }
      */

      if (data.role === 'client') {
        window.location.href = '/client/dashboard/';
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
