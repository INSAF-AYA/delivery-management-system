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

    fetch('/home/auth/login/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Accept': 'application/json'
      },
      credentials: 'same-origin',
      body: formData
    })
    .then(async response => {
      let data = null;
      try { data = await response.json(); } catch (e) {}
      if (!response.ok) {
        if (response.status === 401) throw new Error((data && data.error) ? data.error : 'invalid_credentials');
        throw new Error((data && data.error) ? data.error : 'login_failed');
      }
      return data;
    })
    .then(data => {

      /*
        Expected Django response:
        {
          "role": "agent" | "admin"
        }
      */

      // Both admin and agent redirect to the main dashboard (case-insensitive)
      const role = (data.role || '').toLowerCase();
      if (role === 'admin' || role === 'agent') {
        window.location.href = '/dashboard/';
      } else {
        alert('Unknown role');
      }

    })
    .catch(error => {
      console.error('Login error:', error.message || error);
      if ((error.message || '').toLowerCase().includes('invalid_credentials')) {
        alert('Email or password incorrect');
      } else {
        alert('Login error. Please try again later.');
      }
    });

  });

})();
