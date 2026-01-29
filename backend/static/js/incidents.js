// Incidents.js - Incidents page functionality

let currentIncidentId = null;
let selectedRow = null;

// CSRF token helper
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('incidentSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            applyFilter();
        });
    }

    // Filter button toggle
    const filterBtn = document.getElementById('filterBtn');
    const filterPanel = document.getElementById('filterPanel');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            if (filterPanel) {
                filterPanel.style.display = filterPanel.style.display === 'none' ? 'block' : 'none';
            }
        });
    }

    // Apply filter button
    const applyFilterBtn = document.getElementById('applyFilterBtn');
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', function() {
            applyFilter();
            if (filterPanel) {
                filterPanel.style.display = 'none';
            }
        });
    }

    // Clear filter button
    const clearFilterBtn = document.getElementById('clearFilterBtn');
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function() {
            document.getElementById('incidentSearch').value = '';
            document.getElementById('filterField').value = 'all';
            document.getElementById('filterValue').value = '';
            applyFilter();
            if (filterPanel) {
                filterPanel.style.display = 'none';
            }
        });
    }

    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });

    // Set today's date as default for add form
    const today = new Date().toISOString().split('T')[0];
    const addDateInput = document.getElementById('addDate');
    if (addDateInput) {
        addDateInput.value = today;
    }
});

// Row selection
function selectRow(row) {
    if (selectedRow) {
        selectedRow.classList.remove('selected');
    }
    selectedRow = row;
    row.classList.add('selected');
    currentIncidentId = row.getAttribute('data-id');
}

// Apply filter to incidents
function applyFilter() {
    const searchTerm = document.getElementById('incidentSearch').value.toLowerCase();
    const filterField = document.getElementById('filterField').value;
    const filterValue = document.getElementById('filterValue').value.toLowerCase();
    
    const tableBody = document.getElementById('incidentsTableBody');
    const rows = tableBody.querySelectorAll('tr');

    rows.forEach(row => {
        // Skip empty rows
        if (row.cells.length < 7) return;
        
        let match = true;

        // Search filter (searches all columns)
        if (searchTerm) {
            const rowText = row.textContent.toLowerCase();
            if (!rowText.includes(searchTerm)) {
                match = false;
            }
        }

        // Field-specific filter
        if (match && filterValue) {
            match = false;
            
            if (filterField === 'all' || filterField === 'id') {
                const idCell = row.cells[0];
                if (idCell && idCell.textContent.toLowerCase().includes(filterValue)) {
                    match = true;
                }
            }
            
            if (!match && (filterField === 'all' || filterField === 'type')) {
                const typeCell = row.cells[1];
                if (typeCell && typeCell.textContent.toLowerCase().includes(filterValue)) {
                    match = true;
                }
            }
            
            if (!match && (filterField === 'all' || filterField === 'priority')) {
                const priorityCell = row.cells[3];
                if (priorityCell && priorityCell.textContent.toLowerCase().includes(filterValue)) {
                    match = true;
                }
            }
            
            if (!match && (filterField === 'all' || filterField === 'status')) {
                const statusCell = row.cells[5];
                if (statusCell && statusCell.textContent.toLowerCase().includes(filterValue)) {
                    match = true;
                }
            }
        }

        row.style.display = match ? '' : 'none';
    });
}

// Modal functions
function openAddModal() {
    document.getElementById('addIncidentForm').reset();
    // Set default date to today
    document.getElementById('addDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('addModal').classList.add('active');
}

function openViewModal(incidentId) {
    currentIncidentId = incidentId;
    fetch(`/dashboard/incidents/${incidentId}/json/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const inc = data.incident;
                const statusBadge = getStatusBadge(inc.status);
                const priorityBadge = getPriorityBadge(inc.priority);
                document.getElementById('viewIncidentDetails').innerHTML = `
                    <div class="detail-row"><strong>Incident ID:</strong> ${inc.id_incident}</div>
                    <div class="detail-row"><strong>Type:</strong> ${inc.type_display || inc.incident_type}</div>
                    <div class="detail-row"><strong>Description:</strong> ${inc.description || '-'}</div>
                    <div class="detail-row"><strong>Priority:</strong> ${priorityBadge}</div>
                    <div class="detail-row"><strong>Status:</strong> ${statusBadge}</div>
                    <div class="detail-row"><strong>Date:</strong> ${inc.date || '-'}</div>
                    <div class="detail-row"><strong>Comments:</strong> ${inc.commentaire || '-'}</div>
                    <div class="detail-row"><strong>Created:</strong> ${inc.created_at ? new Date(inc.created_at).toLocaleString() : '-'}</div>
                    ${inc.resolution_date ? `<div class="detail-row"><strong>Resolved:</strong> ${new Date(inc.resolution_date).toLocaleString()}</div>` : ''}
                `;
                document.getElementById('viewModal').classList.add('active');
            }
        })
        .catch(err => console.error('Error fetching incident:', err));
}

function openEditModal(incidentId) {
    currentIncidentId = incidentId;
    fetch(`/dashboard/incidents/${incidentId}/json/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const inc = data.incident;
                document.getElementById('editIncidentId').value = inc.id_incident;
                document.getElementById('editType').value = inc.incident_type || 'other';
                document.getElementById('editDescription').value = inc.description || '';
                document.getElementById('editPriority').value = inc.priority || 'medium';
                document.getElementById('editStatus').value = inc.status || 'new';
                document.getElementById('editDate').value = inc.date || '';
                document.getElementById('editCommentaire').value = inc.commentaire || '';
                document.getElementById('editModal').classList.add('active');
            }
        })
        .catch(err => console.error('Error fetching incident:', err));
}

function openDeleteModal(incidentId) {
    currentIncidentId = incidentId;
    document.getElementById('deleteIncidentInfo').textContent = `Incident ID: ${incidentId}`;
    document.getElementById('deleteModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// CRUD operations
function addIncident() {
    const payload = {
        incident_type: document.getElementById('addType').value,
        description: document.getElementById('addDescription').value,
        priority: document.getElementById('addPriority').value,
        status: document.getElementById('addStatus').value,
        date: document.getElementById('addDate').value,
        commentaire: document.getElementById('addCommentaire').value,
    };

    fetch('/dashboard/incidents/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal('addModal');
            location.reload();
        } else {
            alert('Error adding incident: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error adding incident');
    });
}

function saveIncidentChanges() {
    const incidentId = document.getElementById('editIncidentId').value;
    const payload = {
        incident_type: document.getElementById('editType').value,
        description: document.getElementById('editDescription').value,
        priority: document.getElementById('editPriority').value,
        status: document.getElementById('editStatus').value,
        date: document.getElementById('editDate').value,
        commentaire: document.getElementById('editCommentaire').value,
    };

    fetch(`/dashboard/incidents/${incidentId}/edit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal('editModal');
            location.reload();
        } else {
            alert('Error updating incident: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error updating incident');
    });
}

function confirmDelete() {
    fetch(`/dashboard/incidents/${currentIncidentId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal('deleteModal');
            location.reload();
        } else {
            alert('Error deleting incident');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error deleting incident');
    });
}

// Helper functions
function getStatusBadge(status) {
    const badges = {
        'resolved': '<span class="badge success">Resolved</span>',
        'in_progress': '<span class="badge info">In Progress</span>',
        'open': '<span class="badge warning">Open</span>',
        'new': '<span class="badge warning">New</span>',
        'closed': '<span class="badge">Closed</span>',
        'cancelled': '<span class="badge">Cancelled</span>',
    };
    return badges[status] || `<span class="badge">${status}</span>`;
}

function getPriorityBadge(priority) {
    const badges = {
        'critical': '<span class="badge danger">Critical</span>',
        'high': '<span class="badge warning">High</span>',
        'medium': '<span class="badge info">Medium</span>',
        'low': '<span class="badge">Low</span>',
    };
    return badges[priority] || `<span class="badge">${priority}</span>`;
}