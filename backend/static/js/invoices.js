// invoices.js – Corrected & improved version

let currentInvoiceId = null;

/* =========================
   Helpers
========================= */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(c => {
      const cookie = c.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
      }
    });
  }
  return cookieValue;
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('active');
}
window.closeModal = closeModal;

function notify(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

/* =========================
   Modal init
========================= */
function initInvoiceModals() {
  try {
    ['addInvoiceModal', 'viewInvoiceModal', 'editInvoiceModal', 'deleteInvoiceModal']
      .forEach(id => {
        const el = document.getElementById(id);
        if (el && el.parentElement !== document.body) {
          document.body.appendChild(el);
        }
      });

    // Click outside modal
    document.addEventListener('click', e => {
      const modal = e.target.closest('.modal.active');
      if (modal && e.target === modal) closeModal(modal.id);
    });

    // Escape key
    if (!window.__invoiceEscBound) {
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
          document.querySelectorAll('.modal.active')
            .forEach(m => closeModal(m.id));
        }
      });
      window.__invoiceEscBound = true;
    }
  } catch (err) {
    console.error('initInvoiceModals error', err);
  }
}

/* =========================
   Open modals
========================= */
window.openAddModal = function () {
  ['addClient', 'addAmount', 'addStatus', 'addDate'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('addInvoiceModal')?.classList.add('active');
};

window.openViewModal = function (invoiceId) {
  fetch(`/dashboard/invoices/${invoiceId}/json/`)
    .then(r => r.json())
    .then(data => {
      if (!data.success) return notify('Unable to fetch invoice', 'error');

      const inv = data.invoice;
      const container = document.getElementById('viewInvoiceDetails');
      if (!container) return;

      container.innerHTML = '';
      [
        ['ID', inv.id || invoiceId],
        ['Client', inv.client || '-'],
        ['Amount', inv.amount || '-'],
        ['Status', inv.status || '-'],
        ['Date', inv.date || '-']
      ].forEach(([label, value]) => {
        const row = document.createElement('div');
        row.className = 'detail-row';
        const strong = document.createElement('strong');
        strong.textContent = label + ': ';
        row.append(strong, document.createTextNode(value));
        container.appendChild(row);
      });

      const modal = document.getElementById('viewInvoiceModal');
      if (modal) modal.dataset.invoiceId = invoiceId;

      currentInvoiceId = invoiceId;
      modal?.classList.add('active');
    })
    .catch(err => {
      console.error(err);
      notify('Network error', 'error');
    });
};

window.openEditModal = function (invoiceId) {
  fetch(`/dashboard/invoices/${invoiceId}/json/`)
    .then(r => r.json())
    .then(data => {
      if (!data.success) return notify('Unable to fetch invoice', 'error');

      const inv = data.invoice;
      document.getElementById('editInvoiceId')?.setAttribute('value', invoiceId);
      document.getElementById('editClient').value = inv.client || '';
      document.getElementById('editAmount').value = inv.amount || '';
      document.getElementById('editStatus').value = inv.status || 'unpaid';
      document.getElementById('editDate').value = inv.date || '';
      document.getElementById('editInvoiceModal')?.classList.add('active');
    })
    .catch(err => {
      console.error(err);
      notify('Network error', 'error');
    });
};

window.openDeleteModal = function (invoiceId) {
  fetch(`/dashboard/invoices/${invoiceId}/json/`)
    .then(r => r.json())
    .then(data => {
      const info = document.getElementById('deleteInvoiceInfo');
      const hidden = document.getElementById('deleteInvoiceId');
      if (hidden) hidden.value = invoiceId;

      if (data.success && info) {
        const inv = data.invoice;
        info.textContent = `Are you sure you want to delete invoice ${inv.id || invoiceId} (${inv.client || ''})?`;
      }
      document.getElementById('deleteInvoiceModal')?.classList.add('active');
    })
    .catch(err => {
      console.error(err);
      document.getElementById('deleteInvoiceModal')?.classList.add('active');
    });
};

/* =========================
   Actions
========================= */
window.saveInvoiceChanges = function () {
  const idEl = document.getElementById('editInvoiceId');
  if (!idEl || !idEl.value) return;

  const csrftoken = getCookie('csrftoken');
  const payload = {
    client: document.getElementById('editClient').value,
    amount: document.getElementById('editAmount').value,
    status: document.getElementById('editStatus').value,
    date: document.getElementById('editDate').value
  };

  fetch(`/dashboard/invoices/${idEl.value}/edit/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(payload)
  })
    .then(r => r.json())
    .then(resp => {
      if (!resp.success) return notify('Error updating invoice', 'error');

      const row = document.querySelector(`tr[data-id="${idEl.value}"]`);
      if (row) {
        row.cells[1].textContent = resp.invoice.client || '';
        row.cells[2].textContent = resp.invoice.amount || '';
        row.cells[3].innerHTML =
          `<span class="badge ${resp.invoice.status === 'paid' ? 'success' : 'danger'}">${resp.invoice.status}</span>`;
        row.cells[4].textContent = resp.invoice.date || '';
      }

      closeModal('editInvoiceModal');
      notify('Invoice updated');
    })
    .catch(err => {
      console.error(err);
      notify('Network error', 'error');
    });
};

window.confirmInvoiceDelete = function () {
  const id = document.getElementById('deleteInvoiceId')?.value || currentInvoiceId;
  if (!id) return;

  fetch(`/dashboard/invoices/${id}/delete/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  })
    .then(r => r.json())
    .then(resp => {
      if (!resp.success) return notify('Error deleting invoice', 'error');
      document.querySelector(`tr[data-id="${id}"]`)?.remove();
      closeModal('deleteInvoiceModal');
      notify('Invoice deleted');
    })
    .catch(err => {
      console.error(err);
      notify('Network error', 'error');
    });
};

window.downloadInvoice = function (id) {
  const invoiceId = id || currentInvoiceId;
  if (!invoiceId) return notify('Invoice ID not found', 'error');

  fetch(`/dashboard/invoices/${invoiceId}/download/`)
    .then(r => r.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice_${invoiceId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    })
    .catch(err => {
      console.error(err);
      notify('Download failed', 'error');
    });
};

window.exportInvoices = function () {
  fetch('/dashboard/invoices/export/')
    .then(r => r.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'invoices_export.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    })
    .catch(err => {
      console.error(err);
      notify('Export failed', 'error');
    });
};

/* =========================
   Search
========================= */
document.addEventListener('DOMContentLoaded', () => {
  initInvoiceModals();

  document.querySelectorAll('#invoicesTable tbody tr').forEach(row => {
    row.dataset.search = row.textContent.toLowerCase();
  });

  const searchInput = document.getElementById('invoiceSearch');
  searchInput?.addEventListener('input', function () {
    const term = this.value.toLowerCase();
    document.querySelectorAll('#invoicesTable tbody tr')
      .forEach(row => row.style.display = row.dataset.search.includes(term) ? '' : 'none');
  });
});
