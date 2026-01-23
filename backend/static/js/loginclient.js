
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
        'X-CSRFToken': csrftoken,
        'Accept': 'application/json'
      },
      // Ensure cookies (csrf/session) are sent for same-origin requests
      credentials: 'same-origin',
      body: formData
    })
    .then(async response => {
      
      let data = null;
      try {
        data = await response.json();
      } catch (e) {
        
      }

      if (!response.ok) {
        // 401 Unauthorized -> invalid credentials
        if (response.status === 401) {
          throw new Error((data && data.error) ? data.error : 'invalid_credentials');
        }
        throw new Error((data && data.error) ? data.error : 'login_failed');
      }

      return data;
    })
    .then(data => {
      if (data && data.role === 'client') {
        window.location.href = '/client/dashboard/';
        return;
      }

      // Unexpected successful response
      alert('Accès non autorisé');
    })
    .catch(error => {
      console.error('Login error:', error.message || error);
      // Show a user friendly message for common cases
      if ((error.message || '').toLowerCase().includes('invalid_credentials')) {
        alert('Email ou mot de passe incorrect');
      } else {
        alert('Erreur lors de la connexion. Réessayez plus tard.');
      }
    });

  });

})();
