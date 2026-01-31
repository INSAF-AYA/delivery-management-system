// Main JavaScript for SwiftShip Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar navigation highlighting
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all links
            navLinks.forEach(l => l.parentElement.classList.remove('active'));
            
            // Add active class to clicked link
            this.parentElement.classList.add('active');
        });
    });

    console.log('SwiftShip Dashboard initialized successfully!');
});