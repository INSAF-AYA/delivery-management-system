// Shipments.js - Shipments page functionality

let currentShipmentId = null;
let selectedRow = null;
let shipmentCounter = 8; // Start from 8 since we have 7 existing shipments

// Sample shipment data (simulating database)
const shipmentsData = {
    'SHP001': {
        id: 'SHP001',
        client: 'Acme Corp',
        origin: 'New York, NY',
        destination: 'Los Angeles, CA',
        status: 'Delivered',
        driver: 'John Smith',
        date: '2025-12-20',
        time: '14:30',
        image: null
    },
    'SHP002': {
        id: 'SHP002',
        client: 'Global Tech',
        origin: 'Chicago, IL',
        destination: 'Houston, TX',
        status: 'In Transit',
        driver: 'Sarah Johnson',
        date: '2025-12-19',
        time: '09:15',
        image: null
    },
    'SHP003': {
        id: 'SHP003',
        client: 'Swift Logistics',
        origin: 'Miami, FL',
        destination: 'Seattle, WA',
        status: 'Pending',
        driver: 'Mike Davis',
        date: '2025-12-18',
        time: '16:45',
        image: null
    },
    'SHP004': {
        id: 'SHP004',
        client: 'Prime Retail',
        origin: 'Boston, MA',
        destination: 'Denver, CO',
        status: 'Failed',
        driver: 'Tom Wilson',
        date: '2025-12-17',
        time: '11:20',
        image: null
    },
    'SHP005': {
        id: 'SHP005',
        client: 'Metro Industries',
        origin: 'Phoenix, AZ',
        destination: 'Atlanta, GA',
        status: 'Delivered',
        driver: 'Emma Brown',
        date: '2025-12-16',
        time: '13:10',
        image: null
    },
    'SHP006': {
        id: 'SHP006',
        client: 'Ocean Freight Co',
        origin: 'San Diego, CA',
        destination: 'Portland, OR',
        status: 'In Transit',
        driver: 'James Taylor',
        date: '2025-12-15',
        time: '08:00',
        image: null
    },
    'SHP007': {
        id: 'SHP007',
        client: 'United Supplies',
        origin: 'Dallas, TX',
        destination: 'Philadelphia, PA',
        status: 'Delivered',
        driver: 'Lisa Anderson',
        date: '2025-12-14',
        time: '15:55',
        image: null
    }
};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('shipmentSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            filterShipments(e.target.value);
        });
    }

    // Filter button
    const filterBtn = document.getElementById('filterBtn');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            const searchValue = document.getElementById('shipmentSearch').value;
            filterShipments(searchValue);
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
    // Remove selection from previously selected row
    if (selectedRow) {
        selectedRow.classList.remove('selected');
    }
    
    // Select new row
    row.classList.add('selected');
    selectedRow = row;
    currentShipmentId = row.getAttribute('data-id');
}

// Filter shipments by client name
function filterShipments(searchTerm) {
    const tableBody = document.getElementById('shipmentsTableBody');
    const rows = tableBody.querySelectorAll('tr');
    const term = searchTerm.toLowerCase();

    rows.forEach(row => {
        const clientCell = row.cells[1]; // Client column
        if (clientCell) {
            const clientName = clientCell.textContent.toLowerCase();
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
    document.getElementById('addClient').value = '';
    document.getElementById('addOrigin').value = '';
    document.getElementById('addDestination').value = '';
    document.getElementById('addStatus').value = 'Pending';
    document.getElementById('addDriver').value = '';
    document.getElementById('addDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('addTime').value = new Date().toTimeString().slice(0, 5);
    
    document.getElementById('addModal').classList.add('active');
}

// Open Edit Modal from Toolbar
function openEditModalFromToolbar() {
    if (!currentShipmentId) {
        alert('Veuillez sélectionner une ligne à modifier.');
        return;
    }
    openEditModal(currentShipmentId);
}

// Open Delete Modal from Toolbar
function openDeleteModalFromToolbar() {
    if (!currentShipmentId) {
        alert('Veuillez sélectionner une ligne à supprimer.');
        return;
    }
    openDeleteModal(currentShipmentId);
}

// Open View Modal (for images)
function openViewModal(shipmentId) {
    currentShipmentId = shipmentId;
    const shipment = shipmentsData[shipmentId];
    
    const modal = document.getElementById('viewModal');
    const imageContainer = modal.querySelector('.image-container');
    
    if (shipment && shipment.image) {
        imageContainer.innerHTML = `<img src="${shipment.image}" alt="Shipment Image" style="max-width: 100%; border-radius: 8px;">`;
    } else {
        imageContainer.innerHTML = `
            <div class="no-image">
                <i class="fas fa-image"></i>
                <span>No image available for ${shipmentId}</span>
            </div>
        `;
    }
    
    modal.classList.add('active');
}

// Open Edit Modal
function openEditModal(shipmentId) {
    currentShipmentId = shipmentId;
    const shipment = shipmentsData[shipmentId];
    
    if (shipment) {
        document.getElementById('editShipmentId').value = shipment.id;
        document.getElementById('editClient').value = shipment.client;
        document.getElementById('editOrigin').value = shipment.origin;
        document.getElementById('editDestination').value = shipment.destination;
        document.getElementById('editStatus').value = shipment.status;
        document.getElementById('editDriver').value = shipment.driver;
        document.getElementById('editDate').value = shipment.date;
        document.getElementById('editTime').value = shipment.time || '00:00';
    }
    
    document.getElementById('editModal').classList.add('active');
}

// Open Delete Modal
function openDeleteModal(shipmentId) {
    currentShipmentId = shipmentId;
    document.getElementById('deleteModal').classList.add('active');
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Add new Shipment
function addShipment() {
    const client = document.getElementById('addClient').value;
    const origin = document.getElementById('addOrigin').value;
    const destination = document.getElementById('addDestination').value;
    const status = document.getElementById('addStatus').value;
    const driver = document.getElementById('addDriver').value;
    const date = document.getElementById('addDate').value;
    const time = document.getElementById('addTime').value;

    if (!client || !origin || !destination || !driver || !date || !time) {
        alert('Veuillez remplir tous les champs.');
        return;
    }

    // Generate new ID
    const newId = 'SHP' + String(shipmentCounter).padStart(3, '0');
    shipmentCounter++;

    // Add to data object
    shipmentsData[newId] = {
        id: newId,
        client: client,
        origin: origin,
        destination: destination,
        status: status,
        driver: driver,
        date: date,
        time: time,
        image: null
    };

    // Add new row to table
    const tableBody = document.getElementById('shipmentsTableBody');
    const newRow = document.createElement('tr');
    newRow.setAttribute('data-id', newId);
    newRow.setAttribute('onclick', 'selectRow(this)');
    newRow.innerHTML = `
        <td>${newId}</td>
        <td>${client}</td>
        <td>${origin}</td>
        <td>${destination}</td>
        <td>${getStatusBadge(status)}</td>
        <td>${driver}</td>
        <td>${date}</td>
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
    showNotification('Shipment ajouté avec succès!', 'success');
}

// Save Shipment Changes
function saveShipmentChanges() {
    const shipmentId = document.getElementById('editShipmentId').value;
    
    if (shipmentsData[shipmentId]) {
        // Update data object
        shipmentsData[shipmentId].client = document.getElementById('editClient').value;
        shipmentsData[shipmentId].origin = document.getElementById('editOrigin').value;
        shipmentsData[shipmentId].destination = document.getElementById('editDestination').value;
        shipmentsData[shipmentId].status = document.getElementById('editStatus').value;
        shipmentsData[shipmentId].driver = document.getElementById('editDriver').value;
        shipmentsData[shipmentId].date = document.getElementById('editDate').value;
        shipmentsData[shipmentId].time = document.getElementById('editTime').value;
        
        // Update table row
        const row = document.querySelector(`tr[data-id="${shipmentId}"]`);
        if (row) {
            row.cells[1].textContent = shipmentsData[shipmentId].client;
            row.cells[2].textContent = shipmentsData[shipmentId].origin;
            row.cells[3].textContent = shipmentsData[shipmentId].destination;
            row.cells[4].innerHTML = getStatusBadge(shipmentsData[shipmentId].status);
            row.cells[5].textContent = shipmentsData[shipmentId].driver;
            row.cells[6].textContent = shipmentsData[shipmentId].date;
            row.cells[7].textContent = shipmentsData[shipmentId].time;
        }
        
        closeModal('editModal');
        showNotification('Shipment modifié avec succès!', 'success');
    }
}

// Confirm Delete
function confirmDelete() {
    if (currentShipmentId) {
        // Remove from data object
        delete shipmentsData[currentShipmentId];
        
        // Remove table row
        const row = document.querySelector(`tr[data-id="${currentShipmentId}"]`);
        if (row) {
            row.remove();
        }
        
        // Clear selection
        selectedRow = null;
        currentShipmentId = null;
        
        closeModal('deleteModal');
        showNotification('Shipment supprimé avec succès!', 'danger');
    }
}

// Get status badge HTML
function getStatusBadge(status) {
    const badgeClasses = {
        'Delivered': 'success',
        'In Transit': 'info',
        'Pending': 'warning',
        'Failed': 'danger'
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
