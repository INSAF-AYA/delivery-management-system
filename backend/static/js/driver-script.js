console.log('[DEBUG] driver-script.js loaded');

// Expose a global helper so inline onclick="claimShipment(...)" calls don't fail
// (some templates still use inline handlers). This calls the same logic used
// by the click handler below.
window.claimShipment = function(shipmentId, el) {
    try {
        const btn = (el && el.nodeType === 1) ? el : document.querySelector(`button.claim-bt[data-shipment-id="${shipmentId}"]`);
        if (!btn) return console.warn('claimShipment: button not found', shipmentId);
        // reuse the same click-flow by dispatching a click event on the button
        btn.click();
    } catch (err) {
        console.error('claimShipment error', err);
    }
}

/* =========================
   CSRF HELPER
========================= */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* =========================
   GLOBAL CLICK HANDLER
========================= */
document.addEventListener('click', function (e) {
    // guard the handler so a single unexpected exception doesn't break all clicks
    try {

    /* =========================
       CLAIM SHIPMENT
    ========================= */
    const claimBtn = (e.target && e.target.closest) ? e.target.closest('.claim-bt') : null;
    if (claimBtn) {
        e.preventDefault();

        const shipmentId = claimBtn.dataset.shipmentId;
        if (!shipmentId) return;

        claimBtn.disabled = true;
        const oldText = claimBtn.innerText;
        claimBtn.innerText = 'Claiming...';

        fetch('/driver/claim/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            credentials: 'same-origin',
            body: new URLSearchParams({
                shipment_id: shipmentId
            })
        })
        .then(res => {
            // try parse JSON, but be defensive if server responds with HTML (CSRF, 403 pages)
            const ct = res.headers.get('content-type') || '';
            if (ct.includes('application/json')) return res.json();
            return res.text().then(t => ({ success: false, error: t || 'unexpected_response' }));
        })
        .then(data => {
            if (data && data.success) {
                location.reload();
            } else {
                alert(data && data.error ? data.error : 'Claim failed');
                claimBtn.disabled = false;
                claimBtn.innerText = oldText;
            }
        })
        .catch(() => {
            alert('Network error');
            claimBtn.disabled = false;
            claimBtn.innerText = oldText;
        });

                    if (!btn) return console.warn('claimShipment: button not found', shipmentId);
    }
                    // use dispatchEvent to better mimic user click
                    try {
                        btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    } catch (err) {
                        console.error('claimShipment dispatchEvent failed, falling back to click()', err);
                        btn.click();
                    }
    /* =========================
       UPDATE STATUS
    ========================= */
    const statusBtn = (e.target && e.target.closest) ? e.target.closest('button[data-action]') : null;
    if (!statusBtn) return;

    e.preventDefault();

    const shipmentId = statusBtn.dataset.shipmentId;
    const action = statusBtn.dataset.action;

    if (!shipmentId || !action) return;

    const oldHTML = statusBtn.innerHTML;
    statusBtn.disabled = true;
    statusBtn.innerHTML = 'Processing...';

    fetch('/driver/update_status/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        credentials: 'same-origin',
        body: new URLSearchParams({
            shipment_id: shipmentId,
            action: action
        })
    })
    .then(res => {
        const ct = res.headers.get('content-type') || '';
        if (ct.includes('application/json')) return res.json();
        return res.text().then(t => ({ success: false, error: t || 'unexpected_response' }));
    })
    .then(data => {
        if (data && data.success) {
            location.reload();
        } else {
            alert(data && data.error ? data.error : 'Update failed');
            statusBtn.disabled = false;
            statusBtn.innerHTML = oldHTML;
        }
    })
    .catch(() => {
        alert('Network error');
        statusBtn.disabled = false;
        statusBtn.innerHTML = oldHTML;
    });
    } catch (err) {
        console.error('driver-script click handler error', err);
    }
});
