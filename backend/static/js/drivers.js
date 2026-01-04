// A small, defensive global helper so inline handlers like
// onclick="closeModal('addModal')" work even if scripts run in a different order.
// Quick debug to ensure the script is loaded in the page
try { console.log('drivers.js loaded'); } catch (e) {}
// Minimal getCookie helper (used to read csrftoken). Some pages include this elsewhere,
// but include a local copy here to avoid "getCookie is not defined" errors.
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
// Robust global closeModal: hide by id and remove any active class; reset body overflow
window.closeModal = function(name) {
  try {
    // eslint-disable-next-line no-console
    console.log('closeModal called with:', name);
    const el = document.getElementById(name);
    if (el) {
      // hide either via inline style or active class depending on how it was opened
      try { el.style.display = 'none'; } catch (e) {}
      try { el.classList.remove('active'); } catch (e) {}
    } else {
      // fallback: try common modal ids used across templates
      ['addDriverModal','addModal','deleteDriverModal','deleteModal','viewDriverModal','viewModal','editDriverModal','editModal']
        .forEach(id => {
          const m = document.getElementById(id);
          if (m) {
            try { m.style.display = 'none'; } catch (e) {}
            try { m.classList.remove('active'); } catch (e) {}
          }
        });
    }
    try { document.body.style.overflow = ''; } catch (e) {}
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('closeModal error:', err);
  }
};

// Simple openModal helper used by templates
window.openModal = function(id) {
  try {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  } catch (e) {
    console.error('openModal error', e);
  }
};

// ================= TABLE =================
let selectedRow = null;

function selectRow(row) {
  try {
    if (selectedRow) selectedRow.classList.remove('selected');
    row.classList.add('selected');
    selectedRow = row;
    currentDriverId = row.dataset.id;
  } catch (err) {
    console.error('selectRow error', err);
  }
}

 

document.addEventListener("DOMContentLoaded", () => {

  const addModal = document.getElementById("addDriverModal");
  const deleteModal = document.getElementById("deleteDriverModal");

  const addDriverBtn = document.getElementById("addDriverBtn");
  if (addDriverBtn && addModal) {
    addDriverBtn.onclick = () => {
      addModal.style.display = "block";
      document.body.style.overflow = 'hidden';
    };
  }

  const deleteDriverBtn = document.getElementById("deleteDriverBtn");
  if (deleteDriverBtn && deleteModal) {
    deleteDriverBtn.onclick = () => {
      deleteModal.style.display = "block";
    };
  }

  // Cancel buttons (defensive) — don't prevent default so inline handlers still run
  document.querySelectorAll(".modal-btn.cancel").forEach(btn => {
    btn.addEventListener('click', (ev) => {
      try {
        if (addModal) addModal.style.display = 'none';
        if (deleteModal) deleteModal.style.display = 'none';
        document.body.style.overflow = '';
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('cancel handler error:', err);
      }
    });
  });

  // Close (×) spans inside modals
  document.querySelectorAll('.modal .close').forEach(span => {
    span.addEventListener('click', (ev) => {
      try {
        // find the closest modal container
        const modal = span.closest('.modal');
        if (modal) {
          modal.style.display = 'none';
        }
        document.body.style.overflow = '';
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('close span handler error:', err);
      }
    });
  });

  window.addEventListener('click', e => {
    if (e.target === addModal && addModal) {
      addModal.style.display = 'none';
      document.body.style.overflow = '';
    }
    if (e.target === deleteModal && deleteModal) {
      deleteModal.style.display = 'none';
    }
  });

  const addDriverForm = document.getElementById("addDriverForm");
  if (addDriverForm) {
    addDriverForm.addEventListener('submit', e => {
      // default form POST is intentional for now; just close modal and restore scrolling
      document.body.style.overflow = '';
    });
  }

  const deleteDriverForm = document.getElementById("deleteDriverForm");
  if (deleteDriverForm && deleteModal) {
    // Let the form submit normally (server-side POST will handle delete).
    // We keep a small submit listener only to hide the modal after submit is initiated.
    deleteDriverForm.addEventListener('submit', e => {
      try {
        // allow form to submit; optionally show a loading state
        deleteModal.style.display = 'none';
        document.body.style.overflow = '';
      } catch (err) {
        console.error('delete submit handler error', err);
      }
    });
  }

});
function openViewModal(driverId) {
    fetch(`/dashboard/drivers/${driverId}/json/`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                showNotification('Impossible de récupérer les informations du chauffeur', 'danger');
                return;
            }

            const d = data.driver;
            const container = document.getElementById('viewDriverDetails');
            if (!container) return;

            container.innerHTML = `
                <div class="detail-row"><strong>ID :</strong> ${d.id_chauffeur}</div>
                <div class="detail-row"><strong>Nom :</strong> ${d.nom}</div>
                <div class="detail-row"><strong>Prénom :</strong> ${d.prenom}</div>
                <div class="detail-row"><strong>Email :</strong> ${d.email || '-'}</div>
                <div class="detail-row"><strong>Téléphone :</strong> ${d.telephone || '-'}</div>
                <div class="detail-row"><strong>Permis :</strong> ${d.numero_permis || '-'}</div>
                <div class="detail-row"><strong>Statut :</strong> ${d.statut || '-'}</div>
            `;

            document.getElementById('viewDriverModal').classList.add('active');
            document.getElementById('viewDriverModal').dataset.driverId = d.id_chauffeur;
        })
        .catch(err => {
            console.error(err);
            showNotification('Erreur réseau', 'danger');
        });
}
function openEditModal(driverId) {
    fetch(`/dashboard/drivers/${driverId}/json/`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                showNotification('Erreur chargement chauffeur', 'danger');
                return;
            }

            const d = data.driver;
            document.getElementById('editDriverId').value = d.id_chauffeur;
            document.getElementById('editNom').value = d.nom || '';
            document.getElementById('editPrenom').value = d.prenom || '';
            document.getElementById('editEmail').value = d.email || '';
            document.getElementById('editTelephone').value = d.telephone || '';
            document.getElementById('editPermis').value = d.numero_permis || '';
            // populate statut select if present
            const editStatutEl = document.getElementById('editStatut');
            if (editStatutEl) editStatutEl.value = d.statut || editStatutEl.value;

            document.getElementById('editDriverModal').classList.add('active');
        })
        .catch(err => {
            console.error(err);
            showNotification('Erreur réseau', 'danger');
        });
}
let currentDriverId = null;

function openDeleteModal(driverId) {
    currentDriverId = driverId;

    fetch(`/dashboard/drivers/${driverId}/json/`)
        .then(r => r.json())
        .then(data => {
            const info = document.getElementById('deleteDriverInfo');
            if (data.success && info) {
                const d = data.driver;
                info.textContent = `${d.nom} ${d.prenom} (${d.email || '-'})`;
        // populate hidden input so the POST form sends the driver id
        const hidden = document.getElementById('deleteDriverId');
        if (hidden) hidden.value = d.id_chauffeur;
            }
        })
        .finally(() => {
            document.getElementById('deleteDriverModal').classList.add('active');
        });
}

// ----------------- Search & Filter for Drivers table -----------------
function initDriverSearchFilter() {
  const searchInput = document.getElementById('driverSearch');
  if (searchInput) {
    searchInput.addEventListener('input', e => {
      filterDrivers('all', e.target.value);
    });
  }

  const filterBtn = document.getElementById('filterBtn');
  if (filterBtn) filterBtn.addEventListener('click', toggleFilterPanel);

  const applyFilterBtn = document.getElementById('applyFilterBtn');
  if (applyFilterBtn) applyFilterBtn.addEventListener('click', applyFilter);
  const clearFilterBtn = document.getElementById('clearFilterBtn');
  if (clearFilterBtn) clearFilterBtn.addEventListener('click', clearFilter);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDriverSearchFilter);
} else {
  // If script loaded after DOMContentLoaded, initialize immediately
  try { initDriverSearchFilter(); } catch (e) { console.error('initDriverSearchFilter error', e); }
}

function toggleFilterPanel() {
  const panel = document.getElementById('filterPanel');
  if (!panel) return;
  panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
}

function applyFilter() {
  const field = document.getElementById('filterField')?.value || 'all';
  const value = document.getElementById('filterValue')?.value || '';
  filterDrivers(field, value.trim());
}

function clearFilter() {
  const fieldEl = document.getElementById('filterField');
  const valEl = document.getElementById('filterValue');
  if (fieldEl) fieldEl.value = 'all';
  if (valEl) valEl.value = '';
  const searchInput = document.getElementById('driverSearch');
  if (searchInput) searchInput.value = '';
  filterDrivers('all', '');
}

function filterDrivers(fieldOrTerm, maybeTerm) {
  let field = 'all';
  let term = '';
  if (typeof maybeTerm === 'undefined') {
    term = (fieldOrTerm || '').toString().toLowerCase();
  } else {
    field = (fieldOrTerm || 'all').toString();
    term = (maybeTerm || '').toString().toLowerCase();
  }

  const rows = document.querySelectorAll('table.data-table tbody tr');
  const map = { id:0, nom:1, prenom:2, email:3, telephone:4, permis:5, status:6 };

  rows.forEach(row => {
    if (!row.cells || row.cells.length === 0) return;
    if (!term) { row.style.display = ''; return; }

    if (field === 'all') {
      const id = (row.cells[0]?.textContent || '').toLowerCase();
      const nom = (row.cells[1]?.textContent || '').toLowerCase();
      const prenom = (row.cells[2]?.textContent || '').toLowerCase();
      const email = (row.cells[3]?.textContent || '').toLowerCase();
      const telephone = (row.cells[4]?.textContent || '').toLowerCase();
      const permis = (row.cells[5]?.textContent || '').toLowerCase();
      const status = (row.cells[6]?.textContent || '').toLowerCase();
      const hay = `${id} ${nom} ${prenom} ${email} ${telephone} ${permis} ${status}`;
      row.style.display = hay.includes(term) ? '' : 'none';
    } else {
      const idx = map[field];
      const value = (row.cells[idx]?.textContent || '').toLowerCase();
      row.style.display = value.includes(term) ? '' : 'none';
    }
  });
}

function generateDriverPasswordForCurrentView() {
  const viewModal = document.getElementById('viewDriverModal');
  if (!viewModal) return;
  const driverId = viewModal.dataset.driverId;
  if (!driverId) {
    showNotification('Driver ID introuvable', 'danger');
    return;
  }
  // Prefer cookie but fall back to hidden csrf token input if present
  const csrftoken = getCookie('csrftoken') || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

  fetch(`/dashboard/drivers/${driverId}/reset_password/`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'X-CSRFToken': csrftoken
    }
  }).then(r => {
    // If the request was redirected (e.g. to a login page) or not JSON, treat as permission/auth error
    if (r.status === 403) throw new Error('permission');
    if (r.redirected) throw new Error('permission');
    const ct = r.headers.get('content-type') || '';
    if (!ct.includes('application/json')) throw new Error('bad-response');
    return r.json();
  }).then(data => {
    if (data && data.success) {
      const pwEl = document.getElementById('viewDriverPassword');
      if (pwEl) {
        pwEl.style.display = '';
        pwEl.innerHTML = `<div style="display:flex;align-items:center;gap:8px;"><strong>New password:</strong> <code id="generatedDriverPassword">${data.password}</code> <button class="modal-btn" onclick="copyGeneratedDriverPassword()"><i class="fas fa-copy"></i> Copy</button></div><div style="margin-top:6px;color:#666;font-size:0.9rem;">This password is shown only once. It has been saved (hashed) in the database.</div>`;
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

function copyGeneratedDriverPassword() {
  const el = document.getElementById('generatedDriverPassword');
  if (!el) return;
  const text = el.textContent || el.innerText;
  navigator.clipboard?.writeText(text).then(() => {
    showNotification('Mot de passe copié', 'success');
  }).catch(() => {
    showNotification('Impossible de copier', 'danger');
  });
}
