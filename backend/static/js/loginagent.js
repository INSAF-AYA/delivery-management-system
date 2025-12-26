/*
  LOGIN AGENT / ADMIN — DJANGO READY
  - Frontend validation (Bootstrap)
  - Secure POST with CSRF
  - Redirect based on role
*/

(function () {

  const form = document.getElementById('agentForm');
  if (!form) return;

  // Get CSRF token from cookie (Django standard)
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

    fetch('/api/auth/login/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Invalid credentials');
      }
      return response.json();
    })
    .then(data => {

      /*
        Expected Django response:
        {
          "role": "agent" | "admin"
        }
      */

      if (data.role === 'admin') {
        window.location.href = '/admin/dashboard/';
      } else if (data.role === 'agent') {
        window.location.href = '/agent/dashboard/';
      } else {
        alert('Rôle inconnu');
      }

    })
    .catch(error => {
      alert('Email ou mot de passe incorrect');
      console.error(error);
    });

  });

})();
