// Placeholder for page-specific JS for login.html
// Currently there was no inline JS in the original file, but keeping
// a small file allows adding behavior later and keeps structure consistent.

// Example: add keyboard accessibility enhancement (optional)
document.addEventListener('DOMContentLoaded', function () {
    // Example: focus the first button for keyboard users
    var firstBtn = document.querySelector('.btn-agent, .btn-driver, .btn-client');
    if (firstBtn) firstBtn.setAttribute('tabindex', '0');
});
