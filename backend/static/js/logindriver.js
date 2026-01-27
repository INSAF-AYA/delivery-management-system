

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

    fetch('/api/auth/driver/login/', {
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
          "success": true,
          "role": "driver"
        }
      */

      if (data.success && data.role === 'driver') {
        window.location.href = '/driver/dashboard/';
      } else {
        alert('Access denied');
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
