// Clients.js - Clients page functionality

let currentClientId = null;
let selectedRow = null;
let clientCounter = 9; // Start from 9 since we have 8 existing clients

// Sample client data (simulating database)
const clientsData = {
    'CLT001': {
        id: 'CLT001',
        name: 'Acme Corp',
        email: 'contact@acmecorp.com',
        phone: '+1 (555) 123-4567',
        total: '$125,450',
        shipments: 234,
        status: 'Active',
        time: '10:30',
        image: null
    },
    'CLT002': {
        id: 'CLT002',
        name: 'Global Tech',
        email: 'info@globaltech.io',
        phone: '+1 (555) 234-5678',
        total: '$89,320',
        shipments: 156,
        status: 'Active',
        time: '14:15',
        image: null
    },
    'CLT003': {
        id: 'CLT003',
        name: 'Swift Logistics',
        email: 'hello@swiftlogistics.com',
        phone: '+1 (555) 345-6789',
        total: '$67,890',
        shipments: 98,
        status: 'Pending',
        time: '09:45',
        image: null
    },
    'CLT004': {
        id: 'CLT004',
        name: 'Prime Retail',
        email: 'support@primeretail.com',
        phone: '+1 (555) 456-7890',
        total: '$234,560',
        shipments: 412,
        status: 'Active',
        time: '16:20',
        image: null
    },
    'CLT005': {
        id: 'CLT005',
        name: 'Metro Industries',
        email: 'contact@metroindustries.net',
        phone: '+1 (555) 567-8901',
        total: '$45,230',
        shipments: 67,
        status: 'Inactive',
        time: '11:05',
        image: null
    },
    'CLT006': {
        id: 'CLT006',
        name: 'Ocean Freight Co',
        email: 'sales@oceanfreight.com',
        phone: '+1 (555) 678-9012',
        total: '$178,900',
        shipments: 289,
        status: 'Active',
        time: '13:40',
        image: null
    },
    'CLT007': {
        id: 'CLT007',
        name: 'United Supplies',
        email: 'orders@unitedsupplies.org',
        phone: '+1 (555) 789-0123',
        total: '$92,670',
        shipments: 134,
        status: 'Active',
        time: '08:25',
        image: null
    },
    'CLT008': {
        id: 'CLT008',
        name: 'Express Delivery Inc',
        email: 'admin@expressdelivery.com',
        phone: '+1 (555) 890-1234',
        total: '$156,780',
        shipments: 245,
        status: 'Active',
        time: '17:10',
        image: null
    }
};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('clientSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            filterClients(e.target.value);
        });
    }

    // Filter button
    const filterBtn = document.getElementById('filterBtn');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            const searchValue = document.getElementById('clientSearch').value;
            filterClients(searchValue);
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
});

// Row selection
function selectRow(row) {
    // Remove selection from previously selected row
    if (selectedRow) {
        selectedRow.classList.remove('selected');
    }
    
    // Select new row
    row.classList.add('selected');
    selectedRow = row;
    currentClientId = row.getAttribute('data-id');
}

// Filter clients by name
function filterClients(searchTerm) {
    const tableBody = document.getElementById('clientsTableBody');
    const rows = tableBody.querySelectorAll('tr');
    const term = searchTerm.toLowerCase();

    rows.forEach(row => {
        const nameCell = row.cells[1]; // Name column
        if (nameCell) {
            const clientName = nameCell.textContent.toLowerCase();
            if (clientName.includes(term)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// Open Add Modal
function openAddModal() {
    // Clear form
    document.getElementById('addName').value = '';
    document.getElementById('addEmail').value = '';
    document.getElementById('addPhone').value = '';
    document.getElementById('addTotal').value = '$0';
    document.getElementById('addShipments').value = '0';
    document.getElementById('addStatus').value = 'Active';
    document.getElementById('addTime').value = new Date().toTimeString().slice(0, 5);
    
    document.getElementById('addModal').classList.add('active');
}

// Open Edit Modal from Toolbar
function openEditModalFromToolbar() {
    if (!currentClientId) {
        alert('Veuillez sélectionner une ligne à modifier.');
        return;
    }
    openEditModal(currentClientId);
}

// Open Delete Modal from Toolbar
function openDeleteModalFromToolbar() {
    if (!currentClientId) {
        alert('Veuillez sélectionner une ligne à supprimer.');
        return;
    }
    openDeleteModal(currentClientId);
}

// Open View Modal (for images)
function openViewModal(clientId) {
    currentClientId = clientId;
    const client = clientsData[clientId];
    
    const modal = document.getElementById('viewModal');
    const imageContainer = modal.querySelector('.image-container');
    
    if (client && client.image) {
        imageContainer.innerHTML = `<img src="${client.image}" alt="Client Image" style="max-width: 100%; border-radius: 8px;">`;
    } else {
        imageContainer.innerHTML = `
            <div class="no-image">
                <i class="fas fa-user-circle"></i>
                <span>No image available for ${client ? client.name : clientId}</span>
            </div>
        `;
    }
    
    modal.classList.add('active');
}

// Open Edit Modal
function openEditModal(clientId) {
    currentClientId = clientId;
    const client = clientsData[clientId];
    
    if (client) {
        document.getElementById('editClientId').value = client.id;
        document.getElementById('editName').value = client.name;
        document.getElementById('editEmail').value = client.email;
        document.getElementById('editPhone').value = client.phone;
        document.getElementById('editTotal').value = client.total;
        document.getElementById('editShipments').value = client.shipments;
        document.getElementById('editStatus').value = client.status;
        document.getElementById('editTime').value = client.time || '00:00';
    }
    
    document.getElementById('editModal').classList.add('active');
}

// Open Delete Modal
function openDeleteModal(clientId) {
    currentClientId = clientId;
    document.getElementById('deleteModal').classList.add('active');
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Add new Client
function addClient() {
    const name = document.getElementById('addName').value;
    const email = document.getElementById('addEmail').value;
    const phone = document.getElementById('addPhone').value;
    const total = document.getElementById('addTotal').value;
    const shipments = document.getElementById('addShipments').value;
    const status = document.getElementById('addStatus').value;
    const time = document.getElementById('addTime').value;

    if (!name || !email || !phone || !time) {
        alert('Veuillez remplir tous les champs obligatoires.');
        return;
    }

    // Generate new ID
    const newId = 'CLT' + String(clientCounter).padStart(3, '0');
    clientCounter++;

    // Add to data object
    clientsData[newId] = {
        id: newId,
        name: name,
        email: email,
        phone: phone,
        total: total,
        shipments: parseInt(shipments),
        status: status,
        time: time,
        image: null
    };

    // Add new row to table
    const tableBody = document.getElementById('clientsTableBody');
    const newRow = document.createElement('tr');
    newRow.setAttribute('data-id', newId);
    newRow.setAttribute('onclick', 'selectRow(this)');
    newRow.innerHTML = `
        <td>${newId}</td>
        <td>${name}</td>
        <td>${email}</td>
        <td>${phone}</td>
        <td>${total}</td>
        <td>${shipments}</td>
        <td>${getStatusBadge(status)}</td>
        <td>${time}</td>
        <td>
            <div class="action-btns">
                <button class="action-btn view" title="View Image" onclick="event.stopPropagation(); openViewModal('${newId}');">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn edit" title="Modify" onclick="event.stopPropagation(); openEditModal('${newId}');">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" title="Delete" onclick="event.stopPropagation(); openDeleteModal('${newId}');">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    tableBody.appendChild(newRow);

    closeModal('addModal');
    showNotification('Client ajouté avec succès!', 'success');
}

// Save Client Changes
function saveClientChanges() {
    const clientId = document.getElementById('editClientId').value;
    
    if (clientsData[clientId]) {
        // Update data object
        clientsData[clientId].name = document.getElementById('editName').value;
        clientsData[clientId].email = document.getElementById('editEmail').value;
        clientsData[clientId].phone = document.getElementById('editPhone').value;
        clientsData[clientId].total = document.getElementById('editTotal').value;
        clientsData[clientId].shipments = parseInt(document.getElementById('editShipments').value);
        clientsData[clientId].status = document.getElementById('editStatus').value;
        clientsData[clientId].time = document.getElementById('editTime').value;
        
        // Update table row
        const row = document.querySelector(`tr[data-id="${clientId}"]`);
        if (row) {
            row.cells[1].textContent = clientsData[clientId].name;
            row.cells[2].textContent = clientsData[clientId].email;
            row.cells[3].textContent = clientsData[clientId].phone;
            row.cells[4].textContent = clientsData[clientId].total;
            row.cells[5].textContent = clientsData[clientId].shipments;
            row.cells[6].innerHTML = getStatusBadge(clientsData[clientId].status);
            row.cells[7].textContent = clientsData[clientId].time;
        }
        
        closeModal('editModal');
        showNotification('Client modifié avec succès!', 'success');
    }
}

// Confirm Delete
function confirmDelete() {
    if (currentClientId) {
        // Remove from data object
        delete clientsData[currentClientId];
        
        // Remove table row
        const row = document.querySelector(`tr[data-id="${currentClientId}"]`);
        if (row) {
            row.remove();
        }
        
        // Clear selection
        selectedRow = null;
        currentClientId = null;
        
        closeModal('deleteModal');
        showNotification('Client supprimé avec succès!', 'danger');
    }
}

// Get status badge HTML
function getStatusBadge(status) {
    const badgeClasses = {
        'Active': 'success',
        'Pending': 'warning',
        'Inactive': 'danger'
    };
    return `<span class="badge ${badgeClasses[status] || 'info'}">${status}</span>`;
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles if not exists
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 90px;
                right: 30px;
                padding: 15px 25px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 14px;
                font-weight: 500;
                z-index: 3000;
                animation: slideIn 0.3s ease;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            }
            .notification.success {
                background: #10b981;
                color: white;
            }
            .notification.danger {
                background: #ef4444;
                color: white;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
