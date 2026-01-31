// dashChart.js - Dashboard functionality

document.addEventListener('DOMContentLoaded', function() {
    updateDashboardStats();
    renderDashboardCharts();
    loadRecentActivity();
});

// ---------- Dashboard stats ----------
function updateDashboardStats() {
    fetch('/dashboard/data/')
        .then(res => res.json())
        .then(data => {
            document.getElementById('totalShipments').innerText = data.total_shipments;
            document.getElementById('totalDrivers').innerText = data.total_drivers;
            document.getElementById('totalClients').innerText = data.total_clients;
            document.getElementById('monthlyRevenue').innerText =
                '$' + parseFloat(data.monthly_revenue).toLocaleString(undefined, { maximumFractionDigits: 1 });
        })
        .catch(err => console.error('Error fetching dashboard stats:', err));
}

// ---------- Charts ----------
function renderDashboardCharts() {
    fetch('/dashboard/charts-data/')
        .then(res => res.json())
        .then(data => {
            renderRevenueChart(data.revenue_trends);
            renderStatusChart(data.status_distribution);
            renderWeeklyChart(data.weekly_performance);
        })
        .catch(err => console.error('Error loading charts data:', err));
}

function renderRevenueChart(data) {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Revenue ($)',
                data: data.map(d => d.revenue),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59,130,246,0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

function renderStatusChart(data) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.statut),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: ['#10b981','#3b82f6','#facc15','#ef4444']
            }]
        },
        options: { responsive: true }
    });
}

function renderWeeklyChart(data) {
    const ctx = document.getElementById('weeklyChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.day),
            datasets: [{
                label: 'Shipments',
                data: data.map(d => d.count),
                backgroundColor: '#f97316'
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, precision: 0 } } }
    });
}

// ---------- Recent Activity ----------
function loadRecentActivity() {
    fetch('/dashboard/recent-activity/json/')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('activityTableBody');
            tbody.innerHTML = '';
            data.activities.forEach(act => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${act.time}</td>
                    <td>${act.action}</td>
                    <td>${act.user}</td>
                    <td>${act.details}</td>
                    <td><span class="badge ${getBadgeClass(act.status)}">${act.status}</span></td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => console.error('Error loading recent activity:', err));
}

function getBadgeClass(status) {
    switch(status.toLowerCase()) {
        case 'completed': return 'success';
        case 'pending': return 'info';
        case 'in progress': return 'warning';
        case 'failed': return 'danger';
        default: return 'info';
    }
}
