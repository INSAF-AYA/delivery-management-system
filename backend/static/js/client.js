// Interactivité minimale (commentaires en français)
console.log('client.js loaded');
// Bouton "Track" : récupère le numéro de suivi et affiche une carte de suivi

document.addEventListener('DOMContentLoaded', function () {
    // Track button handler (guarded)
    var trackBtn = document.getElementById('trackBtn');
    if (trackBtn) {
        trackBtn.addEventListener('click', function () {
            var trackingInput = document.getElementById('trackingInput');
            var trackingNumber = trackingInput ? trackingInput.value.trim() : '';
            var output = document.getElementById('trackResult');

            if (!trackingNumber) {
                if (output) output.innerHTML = '<div class="text-danger">Veuillez entrer un numéro de suivi.</div>';
                return;
            }
            // Show immediate feedback while fetching
            if (output) {
                output.innerHTML = `
                    <div class="p-3 text-muted">Chargement... <small>(vérification du serveur)</small></div>
                    <pre id="trackDebug" style="display:none;background:#f6f8fa;padding:8px;border-radius:6px;white-space:pre-wrap"></pre>
                `;
            }

            console.log('client.js: fetching /api/track/ for', trackingNumber);
            fetch('/api/track/?number=' + encodeURIComponent(trackingNumber), { cache: 'no-store' })
                .then(function (res) {
                    console.log('client.js: fetch response', res.status, res);
                    // show status in debug area
                    var dbgEl = document.getElementById('trackDebug');
                    if (dbgEl) {
                        dbgEl.style.display = 'block';
                        dbgEl.textContent = 'HTTP ' + res.status + '\n';
                    }
                    if (!res.ok) return res.text().then(function (t) { throw new Error('HTTP ' + res.status + ' - ' + t); });
                    return res.json();
                })
                .then(function (data) {
                    console.log('client.js: got json', data);
                    var dbgEl = document.getElementById('trackDebug');
                    if (dbgEl) dbgEl.textContent += JSON.stringify(data, null, 2);

                    var shipment = {
                        tracking: data.tracking || trackingNumber,
                        status: data.status || '',
                        estimatedDelivery: data.estimated_delivery || '',
                        progress: data.progress || 0,
                        events: data.events || []
                    };

                    if (!output) return;

                    output.innerHTML = `
            <div class="shipment-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 style="margin:0;">Tracking: <span class="fw-bold">${shipment.tracking}</span>
                            <span class="badge badge-status ms-2">${shipment.status}</span>
                        </h6>
                    </div>
                    <div class="text-end text-muted">Est. Delivery: ${shipment.estimatedDelivery}</div>
                </div>
                <div class="mt-3 p-3" style="background:#f8f9fb; border-radius:8px;">
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="progress-track w-100 me-3">
                            <div class="bar" style="width:${shipment.progress}%"></div>
                        </div>
                        <div style="min-width:40px; text-align:right">${shipment.progress}%</div>
                    </div>
                </div>
                <ul class="mt-3 list-unstyled mb-0">
                    ${shipment.events.map(function (event) {
                        return `
                        <li class="mb-2 d-flex align-items-start">
                            <span class="timeline-dot"></span>
                            <div>
                                <div>${event.description}</div>
                                <div class="text-muted small">${event.date || ''}</div>
                            </div>
                        </li>`;
                    }).join('')}
                </ul>
            </div>`;
                })
                .catch(function (err) {
                    console.error('client.js fetch error', err);
                    if (output) output.innerHTML = '<div class="text-danger">Aucun enregistrement trouvé pour ce numéro.</div>';
                    var dbgEl = document.getElementById('trackDebug');
                    if (dbgEl) dbgEl.textContent += '\nERROR: ' + err.message;
                });
        });
    }

    // Support form: attach only if present
    var supportFormEl = document.getElementById('supportForm');
    if (supportFormEl) {
        supportFormEl.addEventListener('submit', function (e) {
            e.preventDefault();
            alert('Ticket de support soumis (démo)');
            this.reset();
        });
    }
});


function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// View Details: open ticket details modal (global click handler)
document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.view-details');
    if (!btn) return;
    e.preventDefault();
    var ticket = btn.closest('.ticket');
    if (!ticket) return;
    var titleEl = ticket.querySelector('strong');
    var title = titleEl ? titleEl.textContent.trim() : 'Ticket';
    var badge = ticket.querySelector('.badge');
    var status = badge ? badge.textContent.trim() : '';
    var meta = ticket.querySelector('.text-muted.small');
    var id = '';
    var date = '';
    if (meta) {
        var parts = meta.innerText.split('\n').map(function (s) { return s.trim(); }).filter(Boolean);
        parts.forEach(function (p) {
            if (p.toLowerCase().startsWith('ticket id')) {
                id = p.split(':').slice(1).join(':').trim();
            } else if (/\d{4}/.test(p)) {
                date = p;
            }
        });
    }
    var message = ticket.querySelector('p') ? ticket.querySelector('p').textContent.trim() : 'No additional details available.';
    var modalEl = document.getElementById('ticketModal');
    if (!modalEl) return;
    modalEl.querySelector('.modal-title').innerHTML = escapeHtml(title);
    modalEl.querySelector('#ticketId').innerHTML = escapeHtml(id || 'N/A');
    modalEl.querySelector('#ticketStatus').innerHTML = escapeHtml(status || 'N/A');
    modalEl.querySelector('#ticketDate').innerHTML = escapeHtml(date || 'N/A');
    modalEl.querySelector('#ticketMessage').innerHTML = escapeHtml(message);
    var bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();
});
