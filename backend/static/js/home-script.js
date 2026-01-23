console.log('home-script.js loaded');
document.addEventListener('DOMContentLoaded', function () {
    var trackBtn = document.getElementById('trackBtn');
    if (!trackBtn) return;

    trackBtn.addEventListener('click', function () {
        var trackingInput = document.getElementById('trackingInput');
        var trackingNumber = trackingInput ? trackingInput.value.trim() : '';
        var output = document.getElementById('trackResult');

        if (!trackingNumber) {
            if (output) output.innerHTML = '<div class="text-danger">Veuillez entrer un numéro de suivi.</div>';
            return;
        }

    // Call backend API for tracking (moved from /api/track/ to /client/track/)
    fetch('/client/track/?number=' + encodeURIComponent(trackingNumber))
      .then(function (res) {
        if (!res.ok) throw new Error('Not found');
        return res.json();
      })
      .then(function (shipment) {
        var badgeClass = shipment.status === 'Delivered' ? 'badge-delivered' : 'badge-in-transit';

        output.innerHTML = `
        <div class="shipment-card p-3 mt-3 bg-white rounded shadow-sm">

            <!-- Header -->
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 style="margin:0;">
                        Tracking: <span class="fw-bold">${shipment.tracking}</span>
                        <span class="badge badge-status ${badgeClass} ms-2">${shipment.status}</span>
                    </h6>
                </div>
                <div class="text-end text-muted">
                    Est. Delivery: ${shipment.estimated_delivery || ''}
                </div>
            </div>

            <!-- Progress -->
            <div class="mt-3 p-3" style="background:#f8f9fb; border-radius:8px;">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="progress-track w-100 me-3">
                        <div class="bar" style="width:${shipment.progress}%"></div>
                    </div>
                    <div style="min-width:40px; text-align:right">${shipment.progress}%</div>
                </div>
            </div>

            <!-- Timeline -->
            <ul class="mt-3 list-unstyled mb-0">
                ${ (shipment.events || []).map(function (event) {
                    return `
                    <li class="mb-2 d-flex align-items-start">
                        <span class="timeline-dot"></span>
                        <div>
                            <div>${event.description}</div>
                            <div class="text-muted small">${event.date || ''}</div>
                        </div>
                    </li>`;
                }).join('') }
            </ul>

        </div>`;

            })
            .catch(function (err) {
                if (output) output.innerHTML = '<div class="text-danger">Aucun enregistrement trouvé pour ce numéro.</div>';
                console.error(err);
            });
        });
});
