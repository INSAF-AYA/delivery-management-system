// Charts.js - Chart configurations for SwiftShip Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Common chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: true,
                position: 'bottom',
                labels: {
                    padding: 15,
                    font: {
                        size: 12,
                        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                    },
                    usePointStyle: true
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    size: 14,
                    weight: 'bold'
                },
                bodyFont: {
                    size: 13
                },
                cornerRadius: 8
            }
        }
    };

    // ===== Revenue Trends Chart (Line Chart) =====
    const revenueCtx = document.getElementById('revenueChart').getContext('2d');
    const revenueChart = new Chart(revenueCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Revenue ($)',
                data: [32000, 38000, 35000, 42000, 45000, 48000, 52000, 49000, 55000, 58000, 56000, 62000],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#2563eb',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        },
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            },
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    ...commonOptions.plugins.legend,
                    display: false
                }
            }
        }
    });

    // ===== Shipment Status Distribution (Pie Chart) =====
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    const statusChart = new Chart(statusCtx, {
        type: 'pie',
        data: {
            labels: ['Delivered', 'In Transit', 'Pending', 'Failed'],
            datasets: [{
                data: [850, 210, 95, 45],
                backgroundColor: [
                    '#10b981',  // Green for Delivered
                    '#2563eb',  // Blue for In Transit
                    '#f59e0b',  // Orange for Pending
                    '#ef4444'   // Red for Failed
                ],
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 10
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    ...commonOptions.plugins.legend,
                    position: 'right'
                },
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });

    // ===== Weekly Delivery Performance (Bar Chart) =====
    const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
    
    // Get the last 7 days
    const getLast7Days = () => {
        const days = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            days.push(date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }));
        }
        return days;
    };

    const weeklyChart = new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: getLast7Days(),
            datasets: [
                {
                    label: 'Delivered Packages',
                    data: [125, 142, 138, 156, 148, 165, 172],
                    backgroundColor: '#1e40af',
                    borderRadius: 8,
                    borderSkipped: false
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            },
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    ...commonOptions.plugins.legend,
                    display: false
                }
            }
        }
    });

    // ===== Chart Animation and Update Functions =====
    
    // Function to update revenue chart with new data
    function updateRevenueChart(newData) {
        revenueChart.data.datasets[0].data = newData;
        revenueChart.update('active');
    }

    // Function to update status chart with new data
    function updateStatusChart(newData) {
        statusChart.data.datasets[0].data = newData;
        statusChart.update('active');
    }

    // Function to update weekly chart with new data
    function updateWeeklyChart(newData) {
        weeklyChart.data.datasets.forEach((dataset, index) => {
            dataset.data = newData[index];
        });
        weeklyChart.update('active');
    }

    // Simulate real-time updates (optional)
    // Uncomment to enable automatic data updates
    /*
    setInterval(() => {
        // Update status chart with random variations
        const currentData = statusChart.data.datasets[0].data;
        const newData = currentData.map(value => {
            const change = Math.floor(Math.random() * 10) - 5;
            return Math.max(0, value + change);
        });
        updateStatusChart(newData);
    }, 30000); // Update every 30 seconds
    */

    console.log('Charts initialized successfully!');
});

// Export update functions for external use
window.chartUpdaters = {
    updateRevenue: function(data) {
        // Function to update revenue chart from external scripts
        console.log('Updating revenue chart:', data);
    },
    updateStatus: function(data) {
        // Function to update status chart from external scripts
        console.log('Updating status chart:', data);
    },
    updateWeekly: function(data) {
        // Function to update weekly chart from external scripts
        console.log('Updating weekly chart:', data);
    }
};
