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

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        console.log('Searching for:', searchTerm);
        // Add your search logic here
    });

    // Animate stat cards on load
    const statCards = document.querySelectorAll('.stat-card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.5s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    statCards.forEach(card => {
        observer.observe(card);
    });


    // Simulate real-time data updates
    function updateStatCards() {
        const totalShipments = document.getElementById('totalShipments');
        const monthlyRevenue = document.getElementById('monthlyRevenue');
        const successRate = document.getElementById('successRate');
        const activeClients = document.getElementById('activeClients');

        // Random small updates to simulate live data
        setInterval(() => {
            const currentShipments = parseInt(totalShipments.textContent.replace(',', ''));
            if (Math.random() > 0.5) {
                totalShipments.textContent = (currentShipments + 1).toLocaleString();
            }
        }, 10000); // Update every 10 seconds
    }

    updateStatCards();

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#logout' && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Table row highlighting
    const tableRows = document.querySelectorAll('.activity-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            tableRows.forEach(r => r.style.backgroundColor = '');
            this.style.backgroundColor = 'var(--light-blue)';
        });
    });

    console.log('SwiftShip Dashboard initialized successfully!');
});

// Utility function to format numbers
function formatNumber(num) {
    return num.toLocaleString();
}

// Utility function to format currency
function formatCurrency(amount) {
    return '$' + amount.toLocaleString();
}

// Utility function to get random color
function getRandomColor() {
    const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#f97316'];
    return colors[Math.floor(Math.random() * colors.length)];
}
