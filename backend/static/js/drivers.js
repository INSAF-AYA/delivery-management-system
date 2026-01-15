// drivers.js - Use overlay modals (client-style) and driver endpoints
let currentDriverId = null;

// Ensure modals are appended to body so fixed positioning centers relative to viewport
function initDriverModals() {
    try {
        ['addModal','viewModal','editModal','deleteModal'].forEach(id => {
            const el = document.getElementById(id);
            if (el && el.parentElement !== document.body) document.body.appendChild(el);
        });

        // Modal overlay close on click outside - bind once
        document.querySelectorAll('.modal').forEach(overlay => {
            if (overlay.dataset.modalInitialized) return;
            overlay.addEventListener('click', function(e) {
                if (e.target === this) closeModal(this.id);
            });
            overlay.dataset.modalInitialized = '1';
        });

        // ESC key binding - ensure only one global listener
        if (!window.__driversModalKeydownBound) {
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') document.querySelectorAll('.modal.active').forEach(m => closeModal(m.id));
            });
            window.__driversModalKeydownBound = true;
        }
    } catch (err) {
        // Don't let modal init break the rest of the page
        console.error('initDriverModals error', err);
    }
}

// Run immediately (in case DOMContentLoaded already fired or some ancestor scripts alter layout)
initDriverModals();

document.addEventListener('DOMContentLoaded', function() {
    console.log('Drivers page initialized');

    // Search functionality
    const searchInput = document.getElementById('driverSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const term = this.value.toLowerCase();
            const rows = document.querySelectorAll('#driversTableBody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }

    // Filter panel toggle
    const filterBtn = document.getElementById('filterBtn');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            const panel = document.getElementById('filterPanel');
            if (panel) panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        });
    }

    const applyFilterBtn = document.getElementById('applyFilterBtn');
    if (applyFilterBtn) applyFilterBtn.addEventListener('click', function() {
        const field = document.getElementById('filterField').value;
        const value = document.getElementById('filterValue').value.toLowerCase();
        applyAdvancedFilter(field, value);
    });

    const clearFilterBtn = document.getElementById('clearFilterBtn');
    if (clearFilterBtn) clearFilterBtn.addEventListener('click', function() {
        document.getElementById('filterField').value = 'all';
        document.getElementById('filterValue').value = '';
        if (searchInput) searchInput.value = '';
        document.querySelectorAll('#driversTableBody tr').forEach(row => row.style.display = '');
    });

    function applyAdvancedFilter(field, value) {
        const rows = document.querySelectorAll('#driversTableBody tr');
        const columnMap = { id:0, nom:1, prenom:2, email:3, telephone:4, permis:5, status:7 };
        rows.forEach(row => {
            if (field === 'all') {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(value) ? '' : 'none';
            } else {
                const colIndex = columnMap[field];
                const cell = colIndex !== undefined ? row.cells[colIndex] : null;
                row.style.display = cell && cell.textContent.toLowerCase().includes(value) ? '' : 'none';
            }
        });
    }

    // Re-run modal init inside DOMContentLoaded to catch elements that may be injected later
    initDriverModals();

    console.log('Drivers page ready');
});

// Table row selection
window.selectRow = function(row) {
    document.querySelectorAll('#driversTableBody tr').forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');
    currentDriverId = row.dataset.id;
};

// ---------------- MODAL ACTIONS ----------------
function openAddModal() {
    // clear add form fields if present
    ['addNom','addPrenom','addEmail','addTelephone','addPermis','addVehicule','addStatut'].forEach(id => {
        const el = document.getElementById(id); if (el) el.value = '';
    });
    document.getElementById('addModal')?.classList.add('active');
}
window.openAddModal = openAddModal;

window.openViewModal = function(driverId) {
    fetch(`/dashboard/drivers/${driverId}/json/`).then(r => r.json()).then(data => {
        if (!data.success) { alert('Impossible de récupérer les informations du chauffeur'); return; }
        const d = data.driver;
        const container = document.getElementById('viewDriverDetails');
        if (container) container.innerHTML = `
            <div class="detail-row"><strong>ID :</strong> ${d.id_chauffeur}</div>
            <div class="detail-row"><strong>Nom :</strong> ${d.nom}</div>
            <div class="detail-row"><strong>Prénom :</strong> ${d.prenom}</div>
            <div class="detail-row"><strong>Email :</strong> ${d.email || '-'}</div>
            <div class="detail-row"><strong>Téléphone :</strong> ${d.telephone || '-'}</div>
            <div class="detail-row"><strong>Permis :</strong> ${d.numero_permis || '-'}</div>
            <div class="detail-row"><strong>Statut :</strong> ${d.statut || '-'}</div>
        `;
        const viewModal = document.getElementById('viewModal'); if (viewModal) viewModal.dataset.driverId = driverId;
        document.getElementById('viewModal')?.classList.add('active');
    }).catch(err => { console.error(err); alert('Erreur réseau'); });
};

window.openEditModal = function(driverId) {
    fetch(`/dashboard/drivers/${driverId}/json/`).then(r => r.json()).then(data => {
        if (!data.success) { alert('Erreur chargement chauffeur'); return; }
        const d = data.driver;
        document.getElementById('editDriverId').value = d.id_chauffeur;
        document.getElementById('editNom').value = d.nom || '';
        document.getElementById('editPrenom').value = d.prenom || '';
        document.getElementById('editEmail').value = d.email || '';
        document.getElementById('editTelephone').value = d.telephone || '';
        document.getElementById('editPermis').value = d.numero_permis || '';
        const statusSelect = document.getElementById('editStatut'); if (statusSelect) statusSelect.value = d.statut || 'actif';
        document.getElementById('editModal')?.classList.add('active');
    }).catch(err => { console.error(err); alert('Erreur réseau'); });
};

window.openDeleteModal = function(driverId) {
    fetch(`/dashboard/drivers/${driverId}/json/`).then(r => r.json()).then(data => {
        if (data.success) {
            const d = data.driver; const info = document.getElementById('deleteDriverInfo'); if (info) info.textContent = `Êtes-vous sûr de vouloir supprimer ${d.nom} ${d.prenom} ?`;
            const hidden = document.getElementById('deleteDriverId'); if (hidden) hidden.value = driverId;
        } else {
            const row = document.querySelector(`tr[data-id="${driverId}"]`);
            const info = document.getElementById('deleteDriverInfo'); if (row && info) info.textContent = `${row.cells[1]?.textContent || ''} ${row.cells[2]?.textContent || ''}`;
            const hidden = document.getElementById('deleteDriverId'); if (hidden) hidden.value = driverId;
        }
        document.getElementById('deleteModal')?.classList.add('active');
    }).catch(err => {
        console.error(err);
        document.getElementById('deleteModal')?.classList.add('active');
    });
};

function closeModal(id) { document.getElementById(id)?.classList.remove('active'); }
window.closeModal = closeModal;

window.generateDriverPasswordForCurrentView = function() {
    const modal = document.getElementById('viewModal'); if (!modal) return;
    const driverId = modal.dataset.driverId; if (!driverId) { alert('Driver ID introuvable'); return; }
    const csrfToken = getCookie('csrftoken');
    fetch(`/dashboard/drivers/${driverId}/reset_password/`, { method:'POST', headers:{ 'X-CSRFToken': csrfToken } })
    .then(r => r.json()).then(data => {
        if (data.success) {
            const passwordEl = document.getElementById('viewDriverPassword'); if (passwordEl) {
                passwordEl.style.display = 'block';
                passwordEl.innerHTML = `<div class="detail-row"><strong>Nouveau mot de passe :</strong> <code id="generatedDriverPassword">${data.password}</code> <button class="modal-btn" onclick="copyDriverGeneratedPassword()"><i class="fas fa-copy"></i> Copy</button></div>`;
            }
        } else alert('Erreur lors de la génération du mot de passe');
    }).catch(err => { console.error(err); alert('Erreur réseau'); });
};

function copyDriverGeneratedPassword() { const el = document.getElementById('generatedDriverPassword'); if (!el) return; navigator.clipboard.writeText(el.textContent || el.innerText).then(()=>alert('Copié !')).catch(()=>{}); }

function getCookie(name) { let cookieValue=null; if (document.cookie && document.cookie !== '') { const cookies = document.cookie.split(';'); for (let i=0;i<cookies.length;i++){ const cookie = cookies[i].trim(); if (cookie.substring(0,name.length+1)=== (name+'=')) { cookieValue = decodeURIComponent(cookie.substring(name.length+1)); break; } } } return cookieValue; }

// Save changes from edit modal via AJAX
function saveDriverChanges() {
    const id = document.getElementById('editDriverId').value;
    if (!id) return;
    const nom = document.getElementById('editNom').value;
    const prenom = document.getElementById('editPrenom').value;
    const email = document.getElementById('editEmail').value;
    const telephone = document.getElementById('editTelephone').value;
    const numero_permis = document.getElementById('editPermis').value;
    const statut = document.getElementById('editStatut').value;

    const csrftoken = getCookie('csrftoken');
    fetch(`/dashboard/drivers/${id}/edit/`, {
        method: 'POST',
        headers: { 'Content-Type':'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ nom, prenom, email, telephone, numero_permis, statut })
    }).then(r => r.json()).then(resp => {
        if (resp.success) {
            const row = document.querySelector(`tr[data-id="${id}"]`);
            if (row) {
                row.cells[1].textContent = resp.driver.nom || '';
                row.cells[2].textContent = resp.driver.prenom || '';
                row.cells[3].textContent = resp.driver.email || '';
                row.cells[4].textContent = resp.driver.telephone || '';
                row.cells[5].textContent = resp.driver.numero_permis || '';
                row.cells[7].textContent = resp.driver.statut || '';
            }
            closeModal('editModal');
            alert('Chauffeur modifié avec succès');
        } else {
            alert('Erreur lors de la modification');
        }
    }).catch(err => { console.error(err); alert('Erreur réseau'); });
}
window.saveDriverChanges = saveDriverChanges;

function confirmDriverDelete() {
    const id = document.getElementById('deleteDriverId')?.value || currentDriverId;
    if (!id) return;
    const csrftoken = getCookie('csrftoken');
    fetch(`/dashboard/drivers/${id}/delete/`, { method:'POST', headers:{ 'X-CSRFToken': csrftoken } })
    .then(r => r.json()).then(resp => {
        if (resp.success) {
            document.querySelector(`tr[data-id="${id}"]`)?.remove();
            closeModal('deleteModal');
            alert('Chauffeur supprimé');
        } else alert('Erreur lors de la suppression');
    }).catch(err => { console.error(err); alert('Erreur réseau'); });
}
window.confirmDriverDelete = confirmDriverDelete;