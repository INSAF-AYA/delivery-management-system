// Clients.js - Clients page functionality

let currentClientId = null;
let selectedRow = null;
let clientCounter = 9; // Start from 9 since we have 8 existing clients

// ================= INIT =================
document.addEventListener('DOMContentLoaded', function () {

    // Search
    const searchInput = document.getElementById('clientSearch');
    if (searchInput) {
        searchInput.addEventListener('input', e => {
            // quick search: search across main fields
            filterClients('all', e.target.value);
        });
    }

    // Filter button toggles the advanced filter panel
    const filterBtn = document.getElementById('filterBtn');
    if (filterBtn) {
        filterBtn.addEventListener('click', () => {
            toggleFilterPanel();
        });
    }

    // Apply / Clear filter panel buttons (may not exist initially)
    const applyFilterBtn = document.getElementById('applyFilterBtn');
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', () => applyFilter());
    }
    const clearFilterBtn = document.getElementById('clearFilterBtn');
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', () => clearFilter());
    }

    // ✅ Add button (FIXED)
    const addBtn = document.querySelector('.toolbar-btn.add');
    if (addBtn) {
        addBtn.addEventListener('click', function (e) {
            e.preventDefault();
            openAddModal();
        });
    }

    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) closeModal(this.id);
        });
    });

    // Close modal on ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active')
                .forEach(modal => closeModal(modal.id));
        }
    });
});

// ================= TABLE =================
function selectRow(row) {
    if (selectedRow) selectedRow.classList.remove('selected');
    row.classList.add('selected');
    selectedRow = row;
    currentClientId = row.dataset.id;
}

function filterClients(fieldOrTerm, maybeTerm) {
    // Accept two signatures:
    //  - filterClients(term)  -> searches across main fields
    //  - filterClients(field, term) -> searches within a specific field
    let field = 'all';
    let term = '';
    if (typeof maybeTerm === 'undefined') {
        term = (fieldOrTerm || '').toString().toLowerCase();
    } else {
        field = (fieldOrTerm || 'all').toString();
        term = (maybeTerm || '').toString().toLowerCase();
    }

    const rows = document.querySelectorAll('#clientsTableBody tr');

    // map field -> table cell index
    const map = {
        id: 0,
        nom: 1,
        prenom: 2,
        email: 3,
        telephone: 4,
        adresse: 5,
        ville: 6,
        pays: 7
    };

    rows.forEach(row => {
        if (!term) {
            row.style.display = '';
            return;
        }

        if (field === 'all') {
            const id = row.cells[0]?.textContent.toLowerCase() || '';
            const nom = row.cells[1]?.textContent.toLowerCase() || '';
            const prenom = row.cells[2]?.textContent.toLowerCase() || '';
            const email = row.cells[3]?.textContent.toLowerCase() || '';
            const ville = row.cells[6]?.textContent.toLowerCase() || '';
            const pays = row.cells[7]?.textContent.toLowerCase() || '';
            const hay = `${id} ${nom} ${prenom} ${email} ${ville} ${pays}`;
            row.style.display = hay.includes(term) ? '' : 'none';
        } else {
            const idx = map[field];
            const value = row.cells[idx]?.textContent.toLowerCase() || '';
            row.style.display = value.includes(term) ? '' : 'none';
        }
    });
}

function toggleFilterPanel() {
    const panel = document.getElementById('filterPanel');
    if (!panel) return;
    panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
}

function applyFilter() {
    const field = document.getElementById('filterField')?.value || 'all';
    const value = document.getElementById('filterValue')?.value || '';
    filterClients(field, value.trim());
}

function clearFilter() {
    const fieldEl = document.getElementById('filterField');
    const valEl = document.getElementById('filterValue');
    if (fieldEl) fieldEl.value = 'all';
    if (valEl) valEl.value = '';
    const searchInput = document.getElementById('clientSearch');
    if (searchInput) searchInput.value = '';
    filterClients('all', '');
}

// ================= MODALS =================
function openAddModal() {
    const fields = [
        'addNom','addPrenom',
        'addTelephone','addEmail','addAdresse',
        'addVille','addPays'
    ];

    fields.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.value = '';
    });

    document.getElementById('addModal')?.classList.add('active');
}

function openViewModal(clientId) {
    // fetch client details from server and populate view modal
    fetch(`/dashboard/clients/${clientId}/json/`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                showNotification('Impossible de récupérer les informations du client', 'danger');
                return;
            }
            const c = data.client;
            const container = document.getElementById('viewClientDetails');
            if (!container) return;
            container.innerHTML = `
                <div class="detail-row"><strong>ID :</strong> ${c.id_client}</div>
                <div class="detail-row"><strong>Nom :</strong> ${c.nom}</div>
                <div class="detail-row"><strong>Prénom :</strong> ${c.prenom}</div>
                <div class="detail-row"><strong>Email :</strong> ${c.email}</div>
                <div class="detail-row"><strong>Téléphone :</strong> ${c.telephone || '-'}</div>
                <div class="detail-row"><strong>Adresse :</strong> ${c.adresse || '-'}</div>
                <div class="detail-row"><strong>Ville :</strong> ${c.ville || '-'}</div>
                <div class="detail-row"><strong>Pays :</strong> ${c.pays || '-'}</div>
                <div class="detail-row"><strong>Inscription :</strong> ${c.date_inscription ? c.date_inscription.replace('T', ' ').slice(0,16) : ''}</div>
            `;
            document.getElementById('viewModal')?.classList.add('active');
                    // clear any previous generated password display
                    const pwEl = document.getElementById('viewClientPassword');
                    if (pwEl) {
                        pwEl.style.display = 'none';
                        pwEl.innerHTML = '';
                    }
                    // store current client id on the modal for actions like generate password
                    const viewModal = document.getElementById('viewModal');
                    if (viewModal) viewModal.dataset.clientId = c.id_client;
        }).catch(err => {
            console.error(err);
            showNotification('Erreur réseau', 'danger');
        });
}

function generatePasswordForCurrentView() {
    const viewModal = document.getElementById('viewModal');
    if (!viewModal) return;
    const clientId = viewModal.dataset.clientId;
    if (!clientId) {
        showNotification('Client ID introuvable', 'danger');
        return;
    }

    const csrftoken = getCookie('csrftoken');
    fetch(`/dashboard/clients/${clientId}/reset_password/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    }).then(r => {
        if (r.status === 403) throw new Error('permission');
        return r.json();
    }).then(data => {
        if (data && data.success) {
            const pwEl = document.getElementById('viewClientPassword');
            if (pwEl) {
                pwEl.style.display = '';
                pwEl.innerHTML = `<div style="display:flex;align-items:center;gap:8px;"><strong>New password:</strong> <code id="generatedPassword">${data.password}</code> <button class="modal-btn" onclick="copyGeneratedPassword()"><i class="fas fa-copy"></i> Copy</button></div><div style="margin-top:6px;color:#666;font-size:0.9rem;">This password is shown only once. It has been saved (hashed) in the database.</div>`;
            }
            showNotification('Nouveau mot de passe généré', 'success');
        } else {
            showNotification('Impossible de générer le mot de passe', 'danger');
        }
    }).catch(err => {
        console.error(err);
        if (err.message === 'permission') {
            showNotification('Action réservée aux administrateurs', 'danger');
        } else {
            showNotification('Erreur réseau ou permission', 'danger');
        }
    });
}

function copyGeneratedPassword() {
    const el = document.getElementById('generatedPassword');
    if (!el) return;
    const text = el.textContent || el.innerText;
    navigator.clipboard?.writeText(text).then(() => {
        showNotification('Mot de passe copié', 'success');
    }).catch(() => {
        showNotification('Impossible de copier', 'danger');
    });
}

function openEditModalFromToolbar() {
    if (!currentClientId) {
        alert('Veuillez sélectionner une ligne.');
        return;
    }
    openEditModal(currentClientId);
}

function openDeleteModalFromToolbar() {
    if (!currentClientId) {
        alert('Veuillez sélectionner une ligne.');
        return;
    }
    openDeleteModal(currentClientId);
}

function openEditModal(clientId) {
    // Try to fetch the latest client data from server first
    fetch(`/dashboard/clients/${clientId}/json/`)
        .then(r => r.json())
        .then(data => {
            if (data && data.success) {
                const c = data.client;
                document.getElementById('editClientId').value = c.id_client;
                document.getElementById('editNom').value = c.nom || '';
                document.getElementById('editPrenom').value = c.prenom || '';
                document.getElementById('editEmail').value = c.email || '';
                document.getElementById('editPhone').value = c.telephone || '';
                document.getElementById('editAdresse').value = c.adresse || '';
                document.getElementById('editVille').value = c.ville || '';
                document.getElementById('editPays').value = c.pays || '';
                document.getElementById('editDateInscription').value = c.date_inscription ? c.date_inscription.replace('T',' ').slice(0,16) : '';
                document.getElementById('editModal').classList.add('active');
            } else {
                // fallback to reading from table row or demo data
                fillEditFromRowOrDemo(clientId);
            }
        }).catch(err => {
            console.warn('fetch openEditModal failed, falling back to row/demo', err);
            fillEditFromRowOrDemo(clientId);
        });
}

function fillEditFromRowOrDemo(clientId) {
    let c = clientsData && clientsData[clientId];
    if (!c) {
        const row = document.querySelector(`tr[data-id="${clientId}"]`);
        if (!row) return;

        const nom = row.cells[1]?.textContent || '';
        const prenom = row.cells[2]?.textContent || '';
        const email = row.cells[3]?.textContent || '';
        const phone = row.cells[4]?.textContent || '';
        const adresse = row.cells[5]?.textContent || '';
        const ville = row.cells[6]?.textContent || '';
        const pays = row.cells[7]?.textContent || '';
        const dateInscription = row.cells[8]?.textContent || '';

        c = {
            id: clientId,
            nom: nom,
            prenom: prenom,
            email: email,
            telephone: phone,
            adresse: adresse,
            ville: ville,
            pays: pays,
            date_inscription: dateInscription
        };
    }

    document.getElementById('editClientId').value = c.id;
    document.getElementById('editNom').value = c.nom || '';
    document.getElementById('editPrenom').value = c.prenom || '';
    document.getElementById('editEmail').value = c.email || '';
    document.getElementById('editPhone').value = c.telephone || '';
    document.getElementById('editAdresse').value = c.adresse || '';
    document.getElementById('editVille').value = c.ville || '';
    document.getElementById('editPays').value = c.pays || '';
    document.getElementById('editDateInscription').value = c.date_inscription || '';

    document.getElementById('editModal').classList.add('active');
}

function openDeleteModal(clientId) {
    currentClientId = clientId;
    // try to fetch client name for a clearer confirmation message
    fetch(`/dashboard/clients/${clientId}/json/`).then(r => r.json()).then(data => {
        if (data && data.success) {
            const c = data.client;
            const info = document.getElementById('deleteClientInfo');
            if (info) info.textContent = `${c.nom || ''} ${c.prenom || ''} (${c.email || ''})`;
        } else {
            // fallback: try to read from row
            const row = document.querySelector(`tr[data-id="${clientId}"]`);
            const info = document.getElementById('deleteClientInfo');
            if (row && info) info.textContent = `${row.cells[1]?.textContent || ''} ${row.cells[2]?.textContent || ''}`;
        }
    }).catch(err => {
        const row = document.querySelector(`tr[data-id="${clientId}"]`);
        const info = document.getElementById('deleteClientInfo');
        if (row && info) info.textContent = `${row.cells[1]?.textContent || ''} ${row.cells[2]?.textContent || ''}`;
    }).finally(() => {
        document.getElementById('deleteModal').classList.add('active');
    });
}

function closeModal(id) {
    document.getElementById(id)?.classList.remove('active');
}

// ================= ACTIONS =================
function saveClientChanges() {
    const id = document.getElementById('editClientId').value;
    // clientsData is a legacy/demo object that may not be defined in production.
    // Guard against a ReferenceError if it's missing.
    const existsInDemo = (typeof clientsData !== 'undefined') && !!clientsData[id];

    const nom = document.getElementById('editNom').value;
    const prenom = document.getElementById('editPrenom').value;
    const email = document.getElementById('editEmail').value;
    const phone = document.getElementById('editPhone').value;
    const adresse = document.getElementById('editAdresse').value;
    const ville = document.getElementById('editVille').value;
    const pays = document.getElementById('editPays').value;
    const dateInscription = document.getElementById('editDateInscription').value;

    // Send changes to server (persist)
    const csrftoken = getCookie('csrftoken');
    fetch(`/dashboard/clients/${id}/edit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            nom: nom,
            prenom: prenom,
            email: email,
            telephone: phone,
            adresse: adresse,
            ville: ville,
            pays: pays
        })
    }).then(r => r.json())
    .then(resp => {
        if (resp.success) {
            const c = resp.client;
            const row = document.querySelector(`tr[data-id="${id}"]`);
            if (row) {
                row.cells[1].textContent = c.nom || '';
                row.cells[2].textContent = c.prenom || '';
                row.cells[3].textContent = c.email || '';
                row.cells[4].textContent = c.telephone || '';
                row.cells[5].textContent = c.adresse || '';
                row.cells[6].textContent = c.ville || '';
                row.cells[7].textContent = c.pays || '';
                row.cells[8].textContent = c.date_inscription ? c.date_inscription.replace('T', ' ').slice(0,16) : '';
            }
            // keep demo data in sync if present
            if (existsInDemo) {
                const demo = clientsData[id];
                if (demo) {
                    demo.name = `${nom} ${prenom}`.trim();
                    demo.email = email;
                    demo.phone = phone;
                }
            }
            closeModal('editModal');
            showNotification('Client modifié avec succès !', 'success');
        } else {
            showNotification('Erreur lors de la modification', 'danger');
        }
    }).catch(err => {
        console.error(err);
        showNotification('Erreur réseau', 'danger');
    });
}

function confirmDelete() {
    if (!currentClientId) return;

    const id = currentClientId;
    const csrftoken = getCookie('csrftoken');
    fetch(`/dashboard/clients/${id}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    }).then(r => r.json())
    .then(resp => {
        if (resp.success) {
            // remove from table and demo data if present
            document.querySelector(`tr[data-id="${id}"]`)?.remove();
            if (clientsData[id]) delete clientsData[id];
            currentClientId = null;
            selectedRow = null;
            closeModal('deleteModal');
            showNotification('Client supprimé avec succès!', 'danger');
        } else {
            showNotification('Erreur lors de la suppression', 'danger');
        }
    }).catch(err => {
        console.error(err);
        showNotification('Erreur réseau', 'danger');
    });
}

// ================= Helpers =================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ================= UI =================
function getStatusBadge(status) {
    const map = {
        Active: 'success',
        Pending: 'warning',
        Inactive: 'danger'
    };
    return `<span class="badge ${map[status] || 'info'}">${status}</span>`;
}

function showNotification(message, type) {
    const n = document.createElement('div');
    n.className = `notification ${type}`;
    n.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(n);

    setTimeout(() => n.remove(), 3000);
}
