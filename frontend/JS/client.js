// Interactivité minimale (commentaires en français)
// Bouton "Track" : récupère le numéro de suivi et affiche une alerte (démo statique)
// =======================
// Tracking Button Handler
// =======================
document.getElementById('trackBtn').addEventListener('click', function () {

    // 1️⃣ Get tracking number from input
    // (FROM FRONTEND INPUT)
    var trackingNumber = document
        .getElementById('trackingInput')
        .value
        .trim();

    // Container where result will be rendered
    var output = document.getElementById('trackResult');

    // Validation
    if (!trackingNumber) {
        output.innerHTML =
            '<div class="text-danger">Veuillez entrer un numéro de suivi.</div>';
        return;
    }

    // 2️⃣ CALL BACKEND API (TO BE IMPLEMENTED)
    // Example:
    // fetch('/api/track?number=' + trackingNumber)
    //   .then(res => res.json())
    //   .then(data => renderShipment(data));

    // ---------------------------------------
    // TEMPORARY EMPTY DATA (PLACEHOLDER)
    // ---------------------------------------
    var shipment = {
        tracking: '',          // shipment.tracking
        status: '',            // shipment.status
        estimatedDelivery: '', // shipment.estimated_delivery
        progress: 0,           // shipment.progress_percentage
        events: []             // shipment.events[]
    };

    // 3️⃣ Render shipment card (HTML TEMPLATE)
    output.innerHTML = `
        <div class="shipment-card">

            <!-- Header -->
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 style="margin:0;">
                        Tracking:
                        <!-- {{ shipment.tracking }} -->
                        <span class="fw-bold">${shipment.tracking}</span>

                        <!-- Status badge -->
                        <!-- {{ shipment.status }} -->
                        <span class="badge badge-status badge-in-transit ms-2">
                            ${shipment.status}
                        </span>
                    </h6>

                    <div class="text-muted small">
                        <!-- {{ shipment.status_label }} -->
                    </div>
                </div>

                <div class="text-end text-muted">
                    Est. Delivery:
                    <!-- {{ shipment.estimated_delivery }} -->
                    ${shipment.estimatedDelivery}
                </div>
            </div>

            <!-- Progress -->
            <div class="mt-3 p-3" style="background:#f8f9fb; border-radius:8px;">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="progress-track w-100 me-3">
                        <!-- width: {{ shipment.progress }}% -->
                        <div class="bar" style="width:${shipment.progress}%"></div>
                    </div>
                    <div style="min-width:40px; text-align:right">
                        <!-- {{ shipment.progress }}% -->
                        ${shipment.progress}%
                    </div>
                </div>
            </div>

            <!-- Timeline -->
            <ul class="mt-3 list-unstyled mb-0">
                <!-- LOOP: shipment.events -->
                <!--
                shipment.events.forEach(event => {
                -->
                <li class="mb-2">
                    <span style="
                        display:inline-block;
                        width:10px;
                        height:10px;
                        background:#ccc;
                        border-radius:50%;
                        margin-right:.7rem
                    "></span>

                    <!-- {{ event.description }} -->
                    <div></div>

                    <div class="text-muted small">
                        <!-- {{ event.date }} -->
                    </div>
                </li>
                <!-- }) -->
            </ul>

        </div>
    `;
});



function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Formulaire de support : empêche l'envoi réel et réinitialise le formulaire (démo)
document.getElementById('supportForm').addEventListener('submit', function (e) {
    e.preventDefault();
    alert('Ticket de support soumis (démo)');
    this.reset();
});

// View Details: open ticket details modal
document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.view-details');
    if (!btn) return;
    e.preventDefault();
    // find the ticket card container
    var ticket = btn.closest('.ticket');
    if (!ticket) return;
    // Extract fields from the ticket DOM
    var titleEl = ticket.querySelector('strong');
    var title = titleEl ? titleEl.textContent.trim() : 'Ticket';
    var badge = ticket.querySelector('.badge');
    var status = badge ? badge.textContent.trim() : '';
    var meta = ticket.querySelector('.text-muted.small');
    var id = '';
    var date = '';
    if (meta) {
        var parts = meta.innerText.split('\n').map(function (s) { return s.trim(); }).filter(Boolean);
        // parts example: ["Ticket ID: TKT-XXX", "Dec 19, 2024"]
        parts.forEach(function (p) {
            if (p.toLowerCase().startsWith('ticket id')) {
                id = p.split(':').slice(1).join(':').trim();
            } else if (/\d{4}/.test(p)) {
                date = p;
            }
        });
    }
    // Message: try to find a description paragraph (not present in simple template) - fallback
    var message = ticket.querySelector('p') ? ticket.querySelector('p').textContent.trim() : 'No additional details available.';

    // Populate modal
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
